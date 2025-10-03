"""Relationship API routes."""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..repositories.relationship_repository import RelationshipRepository
from ..schemas.relationship import GraphDataResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["relationships"])


@router.get(
    "/projects/{project_id}/relationships",
    response_model=GraphDataResponse,
    status_code=status.HTTP_200_OK,
)
async def get_relationships(
    project_id: UUID,
    epic_id: Optional[UUID] = Query(None, description="Optional epic ID to filter"),
    db: AsyncSession = Depends(get_db),
):
    """Get epic-story relationship graph data.

    Args:
        project_id: Project UUID
        epic_id: Optional epic ID to filter relationships
        db: Database session

    Returns:
        Graph data with nodes (epics + stories) and edges (relationships)

    Raises:
        HTTPException: 404 if project not found or epic_id specified but not found
    """
    # Verify project exists
    from ..repositories.project_repository import ProjectRepository

    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Get graph data
    rel_repo = RelationshipRepository(db)
    graph_data = await rel_repo.get_graph_data(project_id, epic_id)

    # If epic_id was specified but no nodes found, epic doesn't exist
    if epic_id and not graph_data["nodes"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Epic {epic_id} not found",
        )

    return graph_data
