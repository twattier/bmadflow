"""Project API routes."""
import logging
import uuid
from typing import Dict
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..schemas.project import ProjectCreate, ProjectResponse
from ..schemas.sync import SyncStatusResponse, SyncTaskResponse
from ..repositories.project_repository import ProjectRepository
from ..services.sync_service import SyncService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory task tracker (POC approach)
# Maps task_id -> task_status_data
sync_tasks: Dict[str, Dict] = {}
# Maps project_id -> task_id for proper project-based lookup
project_task_map: Dict[uuid.UUID, str] = {}


async def sync_project_background(task_id: str, project_id: uuid.UUID, db: AsyncSession):
    """Background task to sync project from GitHub.

    Args:
        task_id: Unique task identifier
        project_id: Project UUID
        db: Database session
    """
    try:
        # Initialize task status
        sync_tasks[task_id] = {
            "status": "in_progress",
            "processed_count": 0,
            "total_count": 0,
            "current_file": None,
            "error_message": None,
            "retry_allowed": False,
        }
        # Map project to task for status lookup
        project_task_map[project_id] = task_id

        # Run sync service
        sync_service = SyncService(db)
        result = await sync_service.sync_project(
            project_id, task_tracker=sync_tasks[task_id]
        )

        # Update task status on success
        sync_tasks[task_id].update(
            {
                "status": "completed",
                "processed_count": result["processed_count"],
                "total_count": result["total_count"],
                "error_message": None,
                "retry_allowed": False,
            }
        )
        logger.info(f"Sync task {task_id} completed successfully")

    except Exception as e:
        # Update task status on failure
        sync_tasks[task_id].update(
            {
                "status": "failed",
                "error_message": str(e),
                "retry_allowed": True,
            }
        )
        logger.error(f"Sync task {task_id} failed: {e}")


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new project.

    Args:
        project: Project creation data
        db: Database session

    Returns:
        Created project

    Raises:
        HTTPException: 409 if project with same github_url already exists
    """
    project_repo = ProjectRepository(db)

    # Check for duplicate
    existing = await project_repo.get_by_github_url(project.github_url)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with github_url '{project.github_url}' already exists",
        )

    # Extract project name from URL (last segment: owner/repo → repo)
    url_parts = project.github_url.rstrip("/").split("/")
    project_name = url_parts[-1] if url_parts else "unknown"

    # Create project
    created_project = await project_repo.create(
        name=project_name, github_url=project.github_url, sync_status="idle"
    )

    return created_project


@router.post(
    "/{project_id}/sync",
    response_model=SyncTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_sync(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger background sync for a project.

    Args:
        project_id: Project UUID
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync task information

    Raises:
        HTTPException: 404 if project not found, 409 if sync already in progress
    """
    project_repo = ProjectRepository(db)

    # Validate project exists
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}",
        )

    # Check if sync already in progress
    if project.sync_status == "syncing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sync already in progress for this project",
        )

    # Validate GitHub URL is accessible
    from ..services.sync_service import SyncService

    sync_service = SyncService(db)
    try:
        import asyncio

        await asyncio.to_thread(
            sync_service.github_service.validate_repo_url, project.github_url
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or inaccessible GitHub URL: {e}",
        )

    # Generate sync task ID
    task_id = str(uuid.uuid4())

    # Update project status to syncing
    await project_repo.update(project_id, sync_status="syncing")

    # Map project to task before starting background task
    project_task_map[project_id] = task_id

    # Add background task
    background_tasks.add_task(sync_project_background, task_id, project_id, db)

    return SyncTaskResponse(sync_task_id=task_id, message="Sync started")


@router.get("/{project_id}/sync-status", response_model=SyncStatusResponse)
async def get_sync_status(project_id: uuid.UUID):
    """Get sync status for a project.

    Args:
        project_id: Project UUID

    Returns:
        Sync status information

    Raises:
        HTTPException: 404 if no sync task found for project
    """
    # Look up task ID for this project
    task_id = project_task_map.get(project_id)
    if not task_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sync task found for project {project_id}",
        )

    # Get task status
    task_status = sync_tasks.get(task_id)
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sync task {task_id} not found in tracker",
        )

    return SyncStatusResponse(
        status=task_status["status"],
        processed_count=task_status["processed_count"],
        total_count=task_status["total_count"],
        error_message=task_status.get("error_message"),
        retry_allowed=task_status.get("retry_allowed", False),
    )
