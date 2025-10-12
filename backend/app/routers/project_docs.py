"""ProjectDoc API router for CRUD operations."""

from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_doc import ProjectDocRepository
from app.schemas.project_doc import (
    ProjectDocCreate,
    ProjectDocResponse,
    ProjectDocUpdate,
    SyncStatusResponse,
)
from app.services.docling_service import DoclingService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService
from app.services.project_doc_service import ProjectDocService

router = APIRouter(prefix="/api", tags=["project-docs"])


@router.post(
    "/projects/{project_id}/docs",
    response_model=ProjectDocResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_doc(
    project_id: UUID, data: ProjectDocCreate, db: AsyncSession = Depends(get_db)
) -> ProjectDocResponse:
    """Create a new ProjectDoc for a Project."""
    repo = ProjectDocRepository()
    project_doc = await repo.create(db, project_id, data)
    return project_doc


@router.get("/projects/{project_id}/docs", response_model=List[ProjectDocResponse])
async def list_project_docs(
    project_id: UUID, db: AsyncSession = Depends(get_db)
) -> List[ProjectDocResponse]:
    """List all ProjectDocs for a Project ordered by created_at DESC."""
    repo = ProjectDocRepository()
    project_docs = await repo.get_all_by_project(db, project_id)
    return project_docs


@router.get("/project-docs/{id}", response_model=ProjectDocResponse)
async def get_project_doc(id: UUID, db: AsyncSession = Depends(get_db)) -> ProjectDocResponse:
    """Get ProjectDoc by ID."""
    repo = ProjectDocRepository()
    project_doc = await repo.get_by_id(db, id)
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProjectDoc {id} not found",
        )
    return project_doc


@router.put("/project-docs/{id}", response_model=ProjectDocResponse)
async def update_project_doc(
    id: UUID, data: ProjectDocUpdate, db: AsyncSession = Depends(get_db)
) -> ProjectDocResponse:
    """Update ProjectDoc by ID."""
    repo = ProjectDocRepository()
    project_doc = await repo.update(db, id, data)
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProjectDoc {id} not found",
        )
    return project_doc


@router.delete("/project-docs/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_doc(id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete ProjectDoc by ID (cascade deletes related Documents)."""
    repo = ProjectDocRepository()
    deleted = await repo.delete(db, id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProjectDoc {id} not found",
        )


@router.post("/project-docs/{id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_project_doc(
    id: UUID, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    """
    Trigger GitHub sync for a ProjectDoc.

    This endpoint initiates a background sync operation that:
    - Fetches repository file tree from GitHub
    - Downloads all supported file types
    - Stores files in documents table (upsert)
    - Updates last_synced_at timestamp

    Returns 202 Accepted immediately, sync executes in background.
    Use GET /project-docs/{id}/sync-status to check progress.
    """
    # Verify ProjectDoc exists
    repo = ProjectDocRepository()
    project_doc = await repo.get_by_id(db, id)
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProjectDoc {id} not found",
        )

    # Initialize services
    github_service = GitHubService()
    document_repo = DocumentRepository(db)
    document_service = DocumentService(document_repo)
    docling_service = DoclingService()
    embedding_service = EmbeddingService(settings.ollama_endpoint_url)
    chunk_repository = ChunkRepository(db)
    service = ProjectDocService(
        repo,
        github_service,
        document_service,
        docling_service,
        embedding_service,
        chunk_repository,
    )

    # Execute sync in background (fire-and-forget pattern for POC)
    background_tasks.add_task(service.sync_project_doc, db, id)

    return {
        "message": "Sync started",
        "project_doc_id": str(id),
        "status": "processing",
    }


@router.get("/project-docs/{id}/sync-status", response_model=SyncStatusResponse)
async def get_sync_status(id: UUID, db: AsyncSession = Depends(get_db)) -> SyncStatusResponse:
    """
    Get sync status for a ProjectDoc.

    Status values:
    - "idle": No sync performed yet (last_synced_at is null)
    - "syncing": Sync in progress (heuristic: last_synced_at < 5 minutes ago)
    - "completed": Sync completed successfully
    - "failed": Sync encountered errors (check logs)

    The message field provides human-readable status for frontend display.
    """
    # Fetch ProjectDoc
    repo = ProjectDocRepository()
    project_doc = await repo.get_by_id(db, id)
    if not project_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProjectDoc {id} not found",
        )

    # Determine status based on timestamps
    if project_doc.last_synced_at is None:
        # Never synced
        status_value = "idle"
        message = "Not synced yet"
    else:
        # Check if sync is recent (within last 5 minutes - heuristic for POC)
        time_since_sync = datetime.now(timezone.utc) - project_doc.last_synced_at
        if time_since_sync < timedelta(minutes=5):
            status_value = "syncing"
            message = "Syncing..."
        else:
            status_value = "completed"
            # Count synced files
            document_repo = DocumentRepository(db)
            doc_count = await document_repo.count_by_project_doc(id)
            message = f"Sync completed successfully. {doc_count} files synced."

            # Check if needs update
            if (
                project_doc.last_github_commit_date
                and project_doc.last_synced_at < project_doc.last_github_commit_date
            ):
                message += " Needs update."

    return SyncStatusResponse(
        status=status_value,
        message=message,
        last_synced_at=project_doc.last_synced_at,
        last_github_commit_date=project_doc.last_github_commit_date,
    )
