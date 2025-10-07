"""Document storage service."""

import logging
from typing import List, Tuple
from uuid import UUID

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.github import FileInfo

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document storage operations."""

    def __init__(self, document_repo: DocumentRepository):
        """Initialize document service with repository."""
        self.document_repo = document_repo

    async def store_document(
        self, project_doc_id: UUID, file_info: FileInfo, content: str, commit_sha: str
    ) -> Document:
        """Store document in database.

        Args:
            project_doc_id: ProjectDoc UUID
            file_info: FileInfo object with file metadata
            content: File content as string
            commit_sha: GitHub commit SHA

        Returns:
            Created/updated Document instance
        """
        # Extract file metadata
        file_name = file_info.path.split("/")[-1]
        file_type = file_name.split(".")[-1] if "." in file_name else "txt"
        file_size = len(content)

        # Store document using upsert
        doc = await self.document_repo.upsert(
            project_doc_id=project_doc_id,
            file_path=file_info.path,
            content=content,
            file_type=file_type,
            file_size=file_size,
            commit_sha=commit_sha,
        )

        logger.info(f"Stored document: {file_info.path} ({file_size} bytes)")

        return doc

    async def store_documents_batch(
        self, project_doc_id: UUID, files: List[Tuple[FileInfo, str, str]]
    ) -> List[Document]:
        """Store multiple documents, continue on individual failures.

        Args:
            project_doc_id: ProjectDoc UUID
            files: List of tuples (FileInfo, content, commit_sha)

        Returns:
            List of successfully stored documents
        """
        stored_docs = []

        for file_info, content, commit_sha in files:
            try:
                doc = await self.store_document(project_doc_id, file_info, content, commit_sha)
                stored_docs.append(doc)
                logger.info(f"✓ Stored: {file_info.path} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"✗ Failed to store {file_info.path}: {e}", exc_info=True)
                # Continue processing remaining files

        logger.info(
            f"Batch storage complete: {len(stored_docs)}/{len(files)} files stored successfully"
        )

        return stored_docs
