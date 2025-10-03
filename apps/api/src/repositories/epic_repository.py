"""Epic repository for database access."""

from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from ..models.extracted_epic import ExtractedEpic
from .base_repository import BaseRepository


class EpicRepository(BaseRepository[ExtractedEpic]):
    """Repository for ExtractedEpic model operations."""

    def __init__(self, db: AsyncSession):
        """Initialize epic repository.

        Args:
            db: Async database session
        """
        super().__init__(ExtractedEpic, db)

    async def get_by_project(self, project_id: UUID) -> List[ExtractedEpic]:
        """Get all epics for a project with joined document data.

        Args:
            project_id: Project UUID

        Returns:
            List of epic instances with document relationship loaded
        """
        query = (
            select(ExtractedEpic)
            .join(ExtractedEpic.document)
            .where(ExtractedEpic.document.has(project_id=project_id))
            .options(joinedload(ExtractedEpic.document))
            .order_by(ExtractedEpic.epic_number)
        )

        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
