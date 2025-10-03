"""Epic API routes."""

import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..repositories.epic_repository import EpicRepository
from ..schemas.epic import EpicListResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["epics"])


@router.get(
    "/epics",
    response_model=List[EpicListResponse],
    status_code=status.HTTP_200_OK,
)
async def get_epics(
    project_id: UUID = Query(..., description="Project UUID (required)"),
    db: AsyncSession = Depends(get_db),
):
    """Get all epics for a project with extracted metadata.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        List of epics with document metadata

    Raises:
        HTTPException: 400 if project_id missing
    """
    epic_repo = EpicRepository(db)

    # Get epics
    epics = await epic_repo.get_by_project(project_id)
    return epics
