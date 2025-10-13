"""Message service for business logic."""

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message import SendMessageResponse
from app.services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)


class MessageService:
    """Service for message business logic and RAG orchestration."""

    def __init__(
        self,
        message_repo: MessageRepository,
        conversation_repo: ConversationRepository,
        chatbot_service: ChatbotService,
    ):
        """Initialize message service with repositories and services.

        Args:
            message_repo: Message repository instance
            conversation_repo: Conversation repository instance
            chatbot_service: Chatbot service instance for RAG
        """
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo
        self.chatbot_service = chatbot_service

    async def send_message(
        self, db: AsyncSession, conversation_id: UUID, user_content: str
    ) -> SendMessageResponse:
        """Send user message and generate AI response via RAG.

        Orchestrates the full message workflow:
        1. Validate conversation exists
        2. Create user message record
        3. Call RAG agent for response
        4. Create assistant message with sources
        5. Update conversation timestamp
        6. Return both messages

        Args:
            db: Database session
            conversation_id: Conversation UUID
            user_content: User message text

        Returns:
            SendMessageResponse with user and assistant messages

        Raises:
            HTTPException: If conversation not found (404) or RAG fails (500)
        """
        # Step 1: Validate conversation exists and retrieve context
        conversation = await self.conversation_repo.get_by_id(db, conversation_id)
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

        project_id = conversation.project_id
        llm_provider_id = conversation.llm_provider_id

        logger.info(
            f"Processing message for conversation {conversation_id}, " f"project {project_id}"
        )

        try:
            # Step 2: Create user message record
            user_message = await self.message_repo.create(
                db=db,
                conversation_id=conversation_id,
                role="user",
                content=user_content,
                sources=None,
            )
            logger.debug(f"Created user message {user_message.id}")

            # Step 3: Call RAG agent for response generation
            rag_response = await self.chatbot_service.generate_rag_response(
                user_message=user_content,
                project_id=project_id,
                conversation_id=conversation_id,
                llm_provider_id=llm_provider_id,
                db=db,
            )

            # Step 4: Convert SourceAttribution to JSONB format
            sources_json = [
                {
                    "document_id": str(source.document_id),
                    "file_path": source.file_path,
                    "file_name": source.file_path.split("/")[-1] if source.file_path else "unknown",
                    "header_anchor": source.header_anchor,
                    "similarity_score": source.similarity_score,
                }
                for source in rag_response.sources
            ]

            logger.info(f"Saving sources_json to database: {sources_json}")

            # Step 5: Create assistant message with sources
            assistant_message = await self.message_repo.create(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=rag_response.response_text,
                sources=sources_json,
            )
            logger.info(
                f"Created assistant message {assistant_message.id} with "
                f"{len(sources_json)} sources. Retrieved sources from DB: {assistant_message.sources}"
            )

            # Step 6: Update conversation timestamp
            await self.conversation_repo.update_timestamp(db, conversation_id)

            logger.info(
                f"Message workflow complete for conversation {conversation_id}: "
                f"user={user_message.id}, assistant={assistant_message.id}"
            )

            # Step 7: Return both messages
            from app.schemas.conversation import MessageResponse

            return SendMessageResponse(
                user_message=MessageResponse.model_validate(user_message),
                assistant_message=MessageResponse.model_validate(assistant_message),
            )

        except HTTPException:
            # Re-raise HTTP exceptions (e.g., from chatbot_service)
            raise
        except Exception as e:
            logger.error(
                f"Failed to process message for conversation {conversation_id}: {e}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail="Failed to generate AI response")
