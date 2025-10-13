"""Conversation service for business logic."""

import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for conversation business logic."""

    def __init__(self, conversation_repo: ConversationRepository):
        """Initialize conversation service with repository.

        Args:
            conversation_repo: Conversation repository instance
        """
        self.conversation_repo = conversation_repo

    async def create_conversation(
        self, db: AsyncSession, project_id: UUID, llm_provider_id: UUID, title: str
    ) -> Conversation:
        """Create a new conversation.

        Args:
            db: Database session
            project_id: UUID of parent project
            llm_provider_id: UUID of LLM provider to use
            title: Conversation title

        Returns:
            Created conversation instance

        Raises:
            HTTPException: If project or LLM provider not found
        """
        try:
            conversation = await self.conversation_repo.create(
                db, project_id, llm_provider_id, title
            )
            logger.info(
                f"Created conversation {conversation.id} for project {project_id} "
                f"with title '{title}'"
            )
            return conversation
        except Exception as e:
            logger.error(
                f"Failed to create conversation for project {project_id}: {e}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail="Failed to create conversation")

    async def get_conversation(self, db: AsyncSession, conversation_id: UUID) -> Conversation:
        """Get conversation with messages.

        Args:
            db: Database session
            conversation_id: Conversation UUID

        Returns:
            Conversation instance with messages

        Raises:
            HTTPException: If conversation not found (404)
        """
        conversation = await self.conversation_repo.get_by_id(db, conversation_id)
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        return conversation

    async def list_conversations(self, db: AsyncSession, project_id: UUID) -> List[Conversation]:
        """List recent conversations for a project.

        Args:
            db: Database session
            project_id: Project UUID

        Returns:
            List of up to 10 most recent conversations
        """
        conversations = await self.conversation_repo.list_by_project(db, project_id)
        logger.info(f"Retrieved {len(conversations)} conversations for project {project_id}")
        return conversations

    async def delete_conversation(self, db: AsyncSession, conversation_id: UUID) -> None:
        """Delete a conversation.

        Args:
            db: Database session
            conversation_id: Conversation UUID

        Raises:
            HTTPException: If conversation not found (404)
        """
        deleted = await self.conversation_repo.delete(db, conversation_id)
        if not deleted:
            logger.warning(f"Conversation {conversation_id} not found for deletion")
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        logger.info(f"Deleted conversation {conversation_id}")
