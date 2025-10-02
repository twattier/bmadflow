"""Repository for ExtractedEpic database operations."""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.extracted_epic import ExtractedEpic
from src.repositories.base_repository import BaseRepository
from src.schemas.extraction_schemas import ExtractedEpicSchema


class ExtractedEpicRepository(BaseRepository[ExtractedEpic]):
    """Repository for managing extracted epic data.

    Extends BaseRepository with specific methods for epic extraction workflow.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(ExtractedEpic, db)

    async def get_by_document_id(self, document_id: UUID) -> Optional[ExtractedEpic]:
        """Get extracted epic by document ID.

        Args:
            document_id: UUID of the source document

        Returns:
            ExtractedEpic instance or None if not found
        """
        result = await self.db.execute(
            select(ExtractedEpic).where(ExtractedEpic.document_id == document_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self, document_id: UUID, schema: ExtractedEpicSchema
    ) -> ExtractedEpic:
        """Create new extraction or update existing one for a document.

        If extraction already exists for document_id, updates it.
        Otherwise, creates new extraction record.

        Args:
            document_id: UUID of the source document
            schema: ExtractedEpicSchema with extracted data

        Returns:
            Created or updated ExtractedEpic instance
        """
        existing = await self.get_by_document_id(document_id)

        if existing:
            # Update existing extraction
            existing.epic_number = schema.epic_number
            existing.title = schema.title
            existing.goal = schema.goal
            existing.status = schema.status or "draft"
            existing.confidence_score = schema.confidence_score
            # Note: story_count will be updated separately based on relationships
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new extraction
            return await self.create(
                document_id=document_id,
                epic_number=schema.epic_number,
                title=schema.title,
                goal=schema.goal,
                status=schema.status or "draft",
                confidence_score=schema.confidence_score,
                story_count=0,  # Will be updated when relationships are created
            )
