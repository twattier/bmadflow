"""Repository for ExtractedStory database operations."""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.extracted_story import ExtractedStory
from src.repositories.base_repository import BaseRepository
from src.schemas.extraction_schemas import ExtractedStorySchema


class ExtractedStoryRepository(BaseRepository[ExtractedStory]):
    """Repository for managing extracted story data.

    Extends BaseRepository with specific methods for story extraction workflow.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(ExtractedStory, db)

    async def get_by_document_id(self, document_id: UUID) -> Optional[ExtractedStory]:
        """Get extracted story by document ID.

        Args:
            document_id: UUID of the source document

        Returns:
            ExtractedStory instance or None if not found
        """
        result = await self.db.execute(
            select(ExtractedStory).where(ExtractedStory.document_id == document_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self, document_id: UUID, schema: ExtractedStorySchema
    ) -> ExtractedStory:
        """Create new extraction or update existing one for a document.

        If extraction already exists for document_id, updates it.
        Otherwise, creates new extraction record.

        Args:
            document_id: UUID of the source document
            schema: ExtractedStorySchema with extracted data

        Returns:
            Created or updated ExtractedStory instance
        """
        existing = await self.get_by_document_id(document_id)

        if existing:
            # Update existing extraction
            existing.role = schema.role
            existing.action = schema.action
            existing.benefit = schema.benefit
            existing.acceptance_criteria = schema.acceptance_criteria
            existing.status = schema.status
            existing.confidence_score = schema.confidence_score
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new extraction
            return await self.create(
                document_id=document_id,
                role=schema.role,
                action=schema.action,
                benefit=schema.benefit,
                acceptance_criteria=schema.acceptance_criteria,
                status=schema.status,
                confidence_score=schema.confidence_score,
            )
