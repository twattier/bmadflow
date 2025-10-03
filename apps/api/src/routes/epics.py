"""Epic API routes."""

import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..repositories.epic_repository import EpicRepository
from ..schemas.epic import EpicResponse, ExtractedEpicData

logger = logging.getLogger(__name__)

router = APIRouter(tags=["epics"])


@router.get(
    "/epics",
    response_model=List[EpicResponse],
    status_code=status.HTTP_200_OK,
)
async def get_epics(
    project_id: UUID = Query(..., description="Project UUID (required)"),
    db: AsyncSession = Depends(get_db),
):
    """Get all epic documents for a project with extracted metadata.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        List of epic documents with nested extracted_epic data

    Raises:
        HTTPException: 400 if project_id missing
    """
    epic_repo = EpicRepository(db)

    # Get epic documents with extracted_epic relationship
    epic_docs = await epic_repo.get_by_project(project_id)

    # Transform to response format
    response = []
    for doc in epic_docs:
        epic_data = {
            "id": doc.id,
            "project_id": doc.project_id,
            "file_path": doc.file_path,
            "content": doc.content,
            "doc_type": doc.doc_type,
            "title": doc.title,
            "excerpt": doc.excerpt,
            "last_modified": doc.last_modified,
        }

        # Add extracted_epic with fallback to default values
        if doc.extracted_epic:
            # Calculate story_count from related_stories field
            story_count = 0
            if doc.extracted_epic.related_stories:
                # related_stories is a comma-separated string like "story-3-1, story-3-2"
                story_count = len([s.strip() for s in doc.extracted_epic.related_stories.split(",") if s.strip()])

            epic_data["extracted_epic"] = ExtractedEpicData(
                status=doc.extracted_epic.status,
                story_count=story_count,
            )
        else:
            # Fallback for documents without extracted data
            epic_data["extracted_epic"] = ExtractedEpicData(
                status="draft", story_count=0
            )

        response.append(EpicResponse(**epic_data))

    return response
