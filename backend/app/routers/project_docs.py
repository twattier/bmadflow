"""ProjectDoc API router for CRUD operations."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.project_doc import ProjectDocRepository
from app.schemas.project_doc import (
    ProjectDocCreate,
    ProjectDocResponse,
    ProjectDocUpdate,
)

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
