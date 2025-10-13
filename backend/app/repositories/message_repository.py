"""Repository layer for Message data access."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    """Repository for Message CRUD operations."""

    async def create(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        role: str,
        content: str,
        sources: Optional[list] = None,
    ) -> Message:
        """Create a new message.

        Args:
            db: Database session
            conversation_id: UUID of parent conversation
            role: Message role ('user' or 'assistant')
            content: Message text content
            sources: Optional list of source attribution dicts (for assistant messages)

        Returns:
            Created message instance

        Raises:
            ValueError: If role is not 'user' or 'assistant'
        """
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

        message = Message(
            conversation_id=conversation_id, role=role, content=content, sources=sources
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    async def list_by_conversation(self, db: AsyncSession, conversation_id: UUID) -> List[Message]:
        """Retrieve all messages for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation UUID

        Returns:
            List of messages ordered by created_at ASC (chronological)
        """
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
