"""Sync service to orchestrate GitHub fetch and database storage."""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from .github_service import GitHubService
from .story_extraction_service import StoryExtractionService
from .epic_extraction_service import EpicExtractionService
from ..repositories.project_repository import ProjectRepository
from ..repositories.document_repository import DocumentRepository
from ..repositories.extracted_story_repository import ExtractedStoryRepository
from ..repositories.extracted_epic_repository import ExtractedEpicRepository
from ..core.config import settings

logger = logging.getLogger(__name__)


def detect_doc_type(file_path: str) -> str:
    """Detect document type from file path.

    Args:
        file_path: Path to the document file

    Returns:
        Document type: scoping/architecture/epic/story/qa/other
    """
    path_lower = file_path.lower()
    if "docs/prd/" in path_lower:
        return "scoping"
    elif "docs/architecture/" in path_lower:
        return "architecture"
    elif "docs/epics/" in path_lower:
        return "epic"
    elif "docs/stories/" in path_lower:
        return "story"
    elif "docs/qa/" in path_lower:
        return "qa"
    else:
        return "other"


def extract_title(content: str) -> str:
    """Extract title from markdown content (first heading).

    Args:
        content: Markdown file content

    Returns:
        Extracted title or fallback value
    """
    # Match first heading (# Title)
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # Fallback: use first non-empty line
    for line in content.split("\n"):
        line = line.strip()
        if line:
            return line[:500]  # Limit to 500 chars

    return "Untitled"


class SyncService:
    """Service to orchestrate project synchronization from GitHub."""

    def __init__(self, db: AsyncSession):
        """Initialize sync service.

        Args:
            db: Async database session
        """
        self.db = db
        self.github_service = GitHubService(token=settings.GITHUB_TOKEN)
        self.project_repo = ProjectRepository(db)
        self.document_repo = DocumentRepository(db)
        self.story_extraction_service = StoryExtractionService(db)
        self.epic_extraction_service = EpicExtractionService(db)
        self.extracted_story_repo = ExtractedStoryRepository(db)
        self.extracted_epic_repo = ExtractedEpicRepository(db)

    async def sync_project(
        self, project_id: UUID, task_tracker: Dict = None
    ) -> Dict[str, int]:
        """Synchronize project from GitHub.

        Args:
            project_id: Project UUID to sync
            task_tracker: Optional task tracker dict for progress updates

        Returns:
            Dict with processed_count and total_count

        Raises:
            ValueError: If project not found or GitHub fetch fails
        """
        # Get project
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")

        # Update project status
        await self.project_repo.update(project_id, sync_status="syncing")

        try:
            # Validate and parse GitHub URL
            owner, repo = await asyncio.to_thread(
                self.github_service.validate_repo_url, project.github_url
            )

            # Fetch all markdown files from GitHub
            logger.info(f"Fetching files from {owner}/{repo}")
            files = await asyncio.to_thread(
                self.github_service.fetch_all_markdown_files, owner, repo
            )

            total_count = len(files)
            processed_count = 0
            failed_files = []

            # Update task tracker if provided
            if task_tracker is not None:
                task_tracker["total_count"] = total_count

            # Process each file
            for file_path, content in files:
                try:
                    # Extract metadata
                    doc_type = detect_doc_type(file_path)
                    title = extract_title(content)
                    excerpt = content[:500] if content else ""  # First 500 chars

                    # Upsert document
                    await self.document_repo.upsert(
                        project_id=project_id,
                        file_path=file_path,
                        content=content,
                        doc_type=doc_type,
                        title=title,
                        excerpt=excerpt,
                        last_modified=datetime.utcnow(),
                    )

                    processed_count += 1

                    # Update task tracker if provided
                    if task_tracker is not None:
                        task_tracker["processed_count"] = processed_count
                        task_tracker["current_file"] = file_path

                    logger.debug(
                        f"Processed {file_path} ({processed_count}/{total_count})"
                    )

                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    failed_files.append((file_path, str(e)))

            # EXTRACTION PHASE: Extract structured data from epic/story documents
            logger.info(f"Starting extraction phase for project {project_id}")

            # Update task tracker to extraction phase
            if task_tracker is not None:
                task_tracker["extraction_phase"] = "extracting"
                task_tracker["extracted_count"] = 0
                task_tracker["extraction_failures"] = 0

            # Fetch all stored documents for this project
            all_documents = await self.document_repo.get_by_project_id(project_id)

            # Filter for epic and story documents
            extractable_docs = [d for d in all_documents if d.doc_type in ('epic', 'story')]
            extraction_total = len(extractable_docs)

            logger.info(f"Found {extraction_total} documents for extraction (epics/stories)")

            # Track extraction metrics
            extraction_results = await self._extract_documents_concurrently(
                extractable_docs, task_tracker
            )

            extracted_count = extraction_results["successfully_extracted"]
            extraction_failures = extraction_results["extraction_failures"]
            average_confidence = extraction_results.get("average_confidence_score", 0.0)

            # Update task tracker to completed
            if task_tracker is not None:
                task_tracker["extraction_phase"] = "completed"

            logger.info(
                f"Extraction completed: {extracted_count}/{extraction_total} successful, "
                f"{extraction_failures} failures, avg confidence: {average_confidence:.2f}"
            )

            # Determine sync success (>90% files processed)
            success_rate = processed_count / total_count if total_count > 0 else 0
            if success_rate >= 0.9:
                # Update project status to idle
                await self.project_repo.update(
                    project_id,
                    sync_status="idle",
                    last_sync_timestamp=datetime.utcnow(),
                )
                logger.info(
                    f"Sync completed for project {project_id}: {processed_count}/{total_count} files"
                )
            else:
                # Update project status to error
                await self.project_repo.update(project_id, sync_status="error")
                error_msg = f"Sync failed: only {processed_count}/{total_count} files processed ({success_rate*100:.1f}%)"
                logger.error(error_msg)
                raise ValueError(error_msg)

            return {
                "processed_count": processed_count,
                "total_count": total_count,
                "failed_files": failed_files,
                "extraction_summary": {
                    "total_documents": extraction_total,
                    "successfully_extracted": extracted_count,
                    "extraction_failures": extraction_failures,
                    "average_confidence_score": average_confidence,
                },
            }

        except Exception as e:
            # Update project status to error
            await self.project_repo.update(project_id, sync_status="error")
            logger.error(f"Sync failed for project {project_id}: {e}")
            raise

    async def _extract_documents_concurrently(
        self, documents: list, task_tracker: Dict = None
    ) -> Dict:
        """Extract documents concurrently with semaphore-based rate limiting.

        Args:
            documents: List of Document models to extract
            task_tracker: Optional task tracker dict for progress updates

        Returns:
            Dict with extraction metrics
        """
        # Limit to 4 concurrent extractions
        semaphore = asyncio.Semaphore(4)
        successfully_extracted = 0
        extraction_failures = 0
        confidence_scores = []

        async def extract_with_limit(document):
            """Extract a single document with semaphore limit."""
            nonlocal successfully_extracted, extraction_failures

            async with semaphore:
                try:
                    logger.info(f"Extracting {document.doc_type}: {document.file_path}")

                    # Call appropriate extraction service based on doc_type
                    if document.doc_type == "story":
                        result = await self.story_extraction_service.extract_story(document)
                        confidence_scores.append(result.confidence_score)
                    elif document.doc_type == "epic":
                        result = await self.epic_extraction_service.extract_epic(document)
                        confidence_scores.append(result.confidence_score)
                    else:
                        logger.warning(f"Unknown doc_type for extraction: {document.doc_type}")
                        return None

                    successfully_extracted += 1

                    # Update task tracker
                    if task_tracker is not None:
                        task_tracker["extracted_count"] = successfully_extracted
                        task_tracker["extraction_failures"] = extraction_failures

                    logger.debug(
                        f"Extracted {document.doc_type} {document.file_path} "
                        f"(confidence: {result.confidence_score:.2f})"
                    )

                    return result

                except Exception as e:
                    extraction_failures += 1

                    # Update task tracker
                    if task_tracker is not None:
                        task_tracker["extraction_failures"] = extraction_failures

                    logger.error(
                        f"Failed to extract {document.doc_type} {document.file_path}: {e}",
                        exc_info=True
                    )
                    # Don't raise - continue with other documents
                    return None

        # Extract all documents concurrently (with semaphore limit)
        logger.info(f"Starting concurrent extraction of {len(documents)} documents (max 4 concurrent)")
        tasks = [extract_with_limit(doc) for doc in documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate average confidence score
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return {
            "successfully_extracted": successfully_extracted,
            "extraction_failures": extraction_failures,
            "average_confidence_score": average_confidence,
            "results": results,
        }
