"""Repository layer for Conversation data access."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation


class ConversationRepository:
    """Repository for Conversation CRUD operations."""

    async def create(
        self, db: AsyncSession, project_id: UUID, llm_provider_id: UUID, title: str
    ) -> Conversation:
        """Create a new conversation.

        Args:
            db: Database session
            project_id: UUID of parent project
            llm_provider_id: UUID of LLM provider to use
            title: Conversation title

        Returns:
            Created conversation instance with LLM provider data
        """
        conversation = Conversation(
            project_id=project_id, llm_provider_id=llm_provider_id, title=title
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation, ["llm_provider"])
        return conversation

    async def get_by_id(self, db: AsyncSession, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation by ID with eager-loaded messages.

        Args:
            db: Database session
            conversation_id: Conversation UUID

        Returns:
            Conversation instance with messages or None if not found
        """
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def list_by_project(
        self, db: AsyncSession, project_id: UUID, limit: int = 10
    ) -> List[Conversation]:
        """List recent conversations for a project.

        Args:
            db: Database session
            project_id: Project UUID
            limit: Maximum number of conversations to return (default 10)

        Returns:
            List of conversations ordered by updated_at DESC with LLM provider data
        """
        result = await db.execute(
            select(Conversation)
            .where(Conversation.project_id == project_id)
            .options(selectinload(Conversation.llm_provider))
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete(self, db: AsyncSession, conversation_id: UUID) -> bool:
        """Delete conversation by ID (cascades to messages).

        Args:
            db: Database session
            conversation_id: Conversation UUID

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(delete(Conversation).where(Conversation.id == conversation_id))
        await db.commit()
        return result.rowcount > 0

    async def update_timestamp(self, db: AsyncSession, conversation_id: UUID) -> None:
        """Update conversation's updated_at timestamp.

        Args:
            db: Database session
            conversation_id: Conversation UUID
        """
        await db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=func.now())
        )
        await db.commit()

    async def update_title(self, db: AsyncSession, conversation_id: UUID, title: str) -> None:
        """Update conversation title.

        Args:
            db: Database session
            conversation_id: Conversation UUID
            title: New conversation title
        """
        await db.execute(
            update(Conversation).where(Conversation.id == conversation_id).values(title=title)
        )
        await db.commit()
