"""Sync service to orchestrate GitHub fetch and database storage."""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from .github_service import GitHubService
from ..repositories.project_repository import ProjectRepository
from ..repositories.document_repository import DocumentRepository
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
            }

        except Exception as e:
            # Update project status to error
            await self.project_repo.update(project_id, sync_status="error")
            logger.error(f"Sync failed for project {project_id}: {e}")
            raise
