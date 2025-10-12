"""ProjectDoc service for sync orchestration."""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from app.database import AsyncSessionLocal
from app.exceptions import GitHubAPIError
from app.models.document import Document
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.project_doc import ProjectDocRepository
from app.schemas.chunk import ChunkCreate
from app.schemas.project_doc import SyncResult
from app.services.docling_service import DoclingService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService

logger = logging.getLogger(__name__)


class ProjectDocService:
    """Service for ProjectDoc operations including sync orchestration."""

    def __init__(
        self,
        project_doc_repo: ProjectDocRepository,
        github_service: GitHubService,
        document_service: DocumentService,
        docling_service: DoclingService,
        embedding_service: EmbeddingService,
        chunk_repository: ChunkRepository,
    ):
        """
        Initialize ProjectDoc service with dependencies.

        Args:
            project_doc_repo: ProjectDoc repository instance
            github_service: GitHub API service instance
            document_service: Document storage service instance
            docling_service: Docling document processing service
            embedding_service: Ollama embedding service
            chunk_repository: Chunk repository for embedding storage
        """
        self.project_doc_repo = project_doc_repo
        self.github_service = github_service
        self.document_service = document_service
        self.docling_service = docling_service
        self.embedding_service = embedding_service
        self.chunk_repository = chunk_repository

    async def sync_project_doc(self, db, project_doc_id: UUID) -> SyncResult:
        """
        Orchestrate full sync pipeline for a ProjectDoc.

        This method:
        1. Fetches file tree from GitHub
        2. Downloads all supported file contents
        3. Stores documents in database
        4. Process and embed documents (Chunk → Embed → Store)
        5. Fetches last commit date
        6. Updates ProjectDoc timestamps

        Pipeline for each document (Step 4):
        - Download → Store Document → Chunk (Docling) → Generate Embeddings (Ollama) → Store Embeddings
        - Parallel processing: 5 files at a time using asyncio.gather()
        - Error handling: Log error, continue sync, return summary with failed_files count

        Args:
            db: Database session
            project_doc_id: UUID of ProjectDoc to sync

        Returns:
            SyncResult with sync statistics, embeddings created, and errors
        """
        start_time = time.time()
        logger.info(f"Starting sync for ProjectDoc {project_doc_id}")

        try:
            # Fetch ProjectDoc
            project_doc = await self.project_doc_repo.get_by_id(db, project_doc_id)
            if not project_doc:
                error_msg = f"ProjectDoc {project_doc_id} not found"
                logger.error(error_msg)
                return SyncResult(
                    success=False,
                    files_synced=0,
                    files_failed=0,
                    errors=[error_msg],
                    duration_seconds=time.time() - start_time,
                )

            # Step 1: Fetch file tree from GitHub
            files = await self.github_service.fetch_repository_tree(
                project_doc.github_url, project_doc.github_folder_path
            )
            logger.info(f"Found {len(files)} files in repository")

            # Step 2: Download file contents
            downloaded_files = []
            errors = []

            for file_info in files:
                try:
                    content, commit_sha = await self.github_service.download_file_content(
                        project_doc.github_url, file_info.path
                    )
                    downloaded_files.append((file_info, content, commit_sha))
                except Exception as e:
                    error_msg = f"Failed to download {file_info.path}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Step 3: Store documents in batch
            stored_docs = await self.document_service.store_documents_batch(
                project_doc_id, downloaded_files
            )

            # Step 4: Process and embed documents (NEW: Embedding Pipeline)
            embeddings_created = 0
            failed_files = []

            # Process in batches of 5 files at a time
            document_batches = self._batch(stored_docs, 5)
            total_docs = len(stored_docs)

            for batch_idx, batch in enumerate(document_batches, 1):
                batch_start = (batch_idx - 1) * 5 + 1
                logger.info(
                    f"Processing batch {batch_idx}/{len(document_batches)} "
                    f"({len(batch)} documents)"
                )

                # Process batch in parallel with error isolation
                tasks = [
                    self._process_and_embed_document(doc, project_doc.project_id) for doc in batch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results and track failures
                for idx, (doc, result) in enumerate(zip(batch, results)):
                    file_idx = batch_start + idx
                    if isinstance(result, Exception):
                        logger.error(
                            f"Failed to embed {doc.file_path}: {result}",
                            exc_info=result,
                        )
                        failed_files.append(doc.file_path)
                        errors.append(f"Embedding failed for {doc.file_path}: {str(result)}")
                    else:
                        embeddings_created += result
                        logger.info(f"Processing file {file_idx}/{total_docs}: {doc.file_path}")

            # Log summary
            success_count = total_docs - len(failed_files)
            logger.info(
                f"Sync complete: {success_count}/{total_docs} files indexed, "
                f"{len(failed_files)} failed"
            )

            # Step 5: Fetch last commit date
            try:
                last_commit_date = await self.github_service.get_last_commit_date(
                    project_doc.github_url, project_doc.github_folder_path
                )
            except GitHubAPIError as e:
                logger.warning(f"Could not fetch last commit date: {e}")
                last_commit_date = datetime.now(timezone.utc)  # Fallback to current time

            # Step 6: Update ProjectDoc timestamps
            # Create update dict manually to avoid Pydantic schema
            update_data = {
                "last_synced_at": datetime.now(timezone.utc),
                "last_github_commit_date": last_commit_date,
            }

            # Update via raw SQLAlchemy
            project_doc.last_synced_at = update_data["last_synced_at"]
            project_doc.last_github_commit_date = update_data["last_github_commit_date"]
            await db.commit()

            duration = time.time() - start_time
            logger.info(
                f"Sync completed: {len(stored_docs)} files stored, "
                f"{len(errors)} errors, {duration:.2f}s"
            )

            # Performance check: warn if sync exceeds 5 minutes
            if duration > 300:
                logger.warning(
                    f"Sync exceeded 5-minute threshold: {duration:.2f}s " f"(threshold: 300s)"
                )

            return SyncResult(
                success=True,
                files_synced=len(stored_docs),
                embeddings_created=embeddings_created,
                files_failed=len(failed_files),
                errors=errors,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Sync failed for ProjectDoc {project_doc_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return SyncResult(
                success=False,
                files_synced=0,
                embeddings_created=0,
                files_failed=len(files) if "files" in locals() else 0,
                errors=[error_msg],
                duration_seconds=duration,
            )

    @staticmethod
    def _batch(items: List, size: int) -> List[List]:
        """Split a list into batches of specified size.

        Args:
            items: List of items to batch
            size: Batch size

        Returns:
            List of batches
        """
        return [items[i : i + size] for i in range(0, len(items), size)]

    async def _process_and_embed_document(self, document: Document, project_id: UUID) -> int:
        """Process single document through embedding pipeline.

        Pipeline: Load content → Chunk (Docling) → Generate Embeddings (Ollama) → Store

        This method creates its own database session to safely run in parallel with other tasks.

        Args:
            document: Document ORM object with content and metadata
            project_id: Project UUID for metadata

        Returns:
            Number of embeddings created

        Raises:
            Exception: If processing fails (caught by caller)
        """
        # Determine file type and process accordingly
        file_type = document.file_type.lower()

        # Load document content and chunk with Docling
        if file_type in ["md", "markdown"]:
            chunks = await self.docling_service.process_markdown(document.content)
        elif file_type == "csv":
            chunks = await self.docling_service.process_csv(document.content)
        elif file_type in ["yaml", "yml", "json"]:
            chunks = await self.docling_service.process_yaml_json(document.content, file_type)
        else:
            logger.warning(f"Unsupported file type: {file_type} for {document.file_path}")
            return 0

        if not chunks:
            logger.warning(f"No chunks generated for {document.file_path}")
            return 0

        # Extract chunk texts for batch embedding
        chunk_texts = [chunk.text for chunk in chunks]

        # Generate embeddings in batch
        embeddings = await self.embedding_service.generate_embeddings_batch(chunk_texts)

        # Build ChunkCreate objects with metadata
        chunk_creates = []
        file_name = document.file_path.split("/")[-1]

        for chunk, embedding in zip(chunks, embeddings):
            chunk_create = ChunkCreate(
                document_id=document.id,
                chunk_text=chunk.text,
                chunk_index=chunk.index,
                embedding=embedding,
                header_anchor=chunk.header_anchor,
                metadata={
                    "file_path": document.file_path,
                    "file_name": file_name,
                    "file_type": document.file_type,
                    "chunk_position": chunk.index,
                    "total_chunks": len(chunks),
                },
            )
            chunk_creates.append(chunk_create)

        # Create a new database session for this parallel task
        async with AsyncSessionLocal() as session:
            chunk_repo = ChunkRepository(session)
            await chunk_repo.create_chunks_batch(chunk_creates, auto_commit=False)
            await session.commit()

        logger.info(f"Embedded {len(embeddings)} chunks from {document.file_path}")
        return len(embeddings)
