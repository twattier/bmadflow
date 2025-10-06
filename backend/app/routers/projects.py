"""Project API router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])
repo = ProjectRepository()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Create a new project.

    Args:
        data: Project creation data
        db: Database session

    Returns:
        Created project

    Raises:
        HTTPException: If validation fails (422)
    """
    project = await repo.create(db, data)
    return project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
) -> List[ProjectResponse]:
    """List all projects ordered by created_at DESC.

    Args:
        db: Database session

    Returns:
        List of all projects
    """
    projects = await repo.get_all(db)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)) -> ProjectResponse:
    """Get project by ID.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        Project details

    Raises:
        HTTPException: 404 if project not found
    """
    project = await repo.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID, data: ProjectUpdate, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Update project by ID.

    Args:
        project_id: Project UUID
        data: Project update data
        db: Database session

    Returns:
        Updated project

    Raises:
        HTTPException: 404 if project not found
    """
    project = await repo.update(db, project_id, data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    """Delete project by ID (cascade deletes related ProjectDocs).

    Args:
        project_id: Project UUID
        db: Database session

    Raises:
        HTTPException: 404 if project not found
    """
    deleted = await repo.delete(db, project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
