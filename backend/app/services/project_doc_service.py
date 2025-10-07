"""ProjectDoc service for sync orchestration."""

import logging
import time
from datetime import datetime, timezone
from uuid import UUID

from app.exceptions import GitHubAPIError
from app.repositories.project_doc import ProjectDocRepository
from app.schemas.project_doc import SyncResult
from app.services.document_service import DocumentService
from app.services.github_service import GitHubService

logger = logging.getLogger(__name__)


class ProjectDocService:
    """Service for ProjectDoc operations including sync orchestration."""

    def __init__(
        self,
        project_doc_repo: ProjectDocRepository,
        github_service: GitHubService,
        document_service: DocumentService,
    ):
        """
        Initialize ProjectDoc service with dependencies.

        Args:
            project_doc_repo: ProjectDoc repository instance
            github_service: GitHub API service instance
            document_service: Document storage service instance
        """
        self.project_doc_repo = project_doc_repo
        self.github_service = github_service
        self.document_service = document_service

    async def sync_project_doc(self, db, project_doc_id: UUID) -> SyncResult:
        """
        Orchestrate full sync pipeline for a ProjectDoc.

        This method:
        1. Fetches file tree from GitHub
        2. Downloads all supported file contents
        3. Stores documents in database
        4. Updates ProjectDoc timestamps

        Args:
            db: Database session
            project_doc_id: UUID of ProjectDoc to sync

        Returns:
            SyncResult with sync statistics and errors
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

            # Step 4: Fetch last commit date
            try:
                last_commit_date = await self.github_service.get_last_commit_date(
                    project_doc.github_url, project_doc.github_folder_path
                )
            except GitHubAPIError as e:
                logger.warning(f"Could not fetch last commit date: {e}")
                last_commit_date = datetime.now(timezone.utc)  # Fallback to current time

            # Step 5: Update ProjectDoc timestamps
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

            return SyncResult(
                success=True,
                files_synced=len(stored_docs),
                files_failed=len(errors),
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
                files_failed=len(files) if "files" in locals() else 0,
                errors=[error_msg],
                duration_seconds=duration,
            )
