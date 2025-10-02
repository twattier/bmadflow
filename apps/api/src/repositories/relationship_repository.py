"""Repository for Relationship database operations."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.models.relationship import Relationship
from src.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class RelationshipRepository(BaseRepository[Relationship]):
    """Repository for managing document relationships.

    Handles epic-to-story relationships and enforces unique constraints.
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(Relationship, db)

    async def create_relationship(
        self,
        parent_doc_id: UUID,
        child_doc_id: UUID,
        relationship_type: str = "contains",
    ) -> Optional[Relationship]:
        """Create a new document relationship.

        Args:
            parent_doc_id: UUID of parent document (e.g., epic)
            child_doc_id: UUID of child document (e.g., story)
            relationship_type: Type of relationship (default: "contains")

        Returns:
            Created Relationship instance, or None if duplicate

        Note:
            Handles unique constraint violations gracefully - logs warning
            and returns None if relationship already exists.
        """
        try:
            return await self.create(
                parent_doc_id=parent_doc_id,
                child_doc_id=child_doc_id,
                relationship_type=relationship_type,
            )
        except IntegrityError:
            # Unique constraint violation - relationship already exists
            logger.warning(
                f"Relationship already exists: {parent_doc_id} -> {child_doc_id} ({relationship_type})"
            )
            await self.db.rollback()
            return None

    async def get_by_parent_doc_id(self, parent_doc_id: UUID) -> List[Relationship]:
        """Get all relationships for a parent document.

        Args:
            parent_doc_id: UUID of parent document

        Returns:
            List of Relationship instances (may be empty)
        """
        result = await self.db.execute(
            select(Relationship).where(Relationship.parent_doc_id == parent_doc_id)
        )
        return list(result.scalars().all())
