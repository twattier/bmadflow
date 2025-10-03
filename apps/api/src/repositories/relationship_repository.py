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

    async def get_graph_data(
        self, project_id: UUID, epic_id: Optional[UUID] = None
    ) -> dict:
        """Get epic-story relationship graph data.

        Args:
            project_id: Project UUID
            epic_id: Optional epic ID to filter relationships

        Returns:
            Dictionary with 'nodes' and 'edges' lists
        """
        from sqlalchemy.orm import joinedload
        from src.models.extracted_epic import ExtractedEpic
        from src.models.extracted_story import ExtractedStory
        from src.models.document import Document

        nodes = []
        edges = []

        # Get epics (filtered by epic_id if provided)
        epic_query = (
            select(ExtractedEpic)
            .join(ExtractedEpic.document)
            .where(Document.project_id == project_id)
            .options(joinedload(ExtractedEpic.document))
        )

        if epic_id:
            epic_query = epic_query.where(ExtractedEpic.id == epic_id)

        epic_result = await self.db.execute(epic_query)
        epics = list(epic_result.unique().scalars().all())

        # Add epic nodes
        epic_doc_ids = set()
        for epic in epics:
            nodes.append(
                {
                    "id": str(epic.id),
                    "title": epic.title,
                    "type": "epic",
                    "status": epic.status,
                    "document_id": str(epic.document_id),
                }
            )
            epic_doc_ids.add(epic.document_id)

        if not epic_doc_ids:
            return {"nodes": nodes, "edges": edges}

        # Get relationships for these epics
        relationship_query = (
            select(Relationship)
            .where(Relationship.parent_doc_id.in_(epic_doc_ids))
            .options(
                joinedload(Relationship.parent_document),
                joinedload(Relationship.child_document),
            )
        )

        rel_result = await self.db.execute(relationship_query)
        relationships = list(rel_result.unique().scalars().all())

        # Get story IDs from relationships
        story_doc_ids = set(rel.child_doc_id for rel in relationships)

        # Get stories
        if story_doc_ids:
            story_query = (
                select(ExtractedStory)
                .where(ExtractedStory.document_id.in_(story_doc_ids))
                .options(joinedload(ExtractedStory.document))
            )

            story_result = await self.db.execute(story_query)
            stories = list(story_result.unique().scalars().all())

            # Add story nodes
            for story in stories:
                title = f"Story: {story.role}" if story.role else "Story"
                nodes.append(
                    {
                        "id": str(story.id),
                        "title": title,
                        "type": "story",
                        "status": story.status or "draft",
                        "document_id": str(story.document_id),
                    }
                )

            # Build edges (map document_id to extracted entity id)
            doc_to_epic = {epic.document_id: epic.id for epic in epics}
            doc_to_story = {story.document_id: story.id for story in stories}

            for rel in relationships:
                source_id = doc_to_epic.get(rel.parent_doc_id)
                target_id = doc_to_story.get(rel.child_doc_id)

                if source_id and target_id:
                    edges.append(
                        {
                            "source_id": str(source_id),
                            "target_id": str(target_id),
                            "type": rel.relationship_type,
                        }
                    )

        return {"nodes": nodes, "edges": edges}
