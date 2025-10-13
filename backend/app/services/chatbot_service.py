"""Chatbot service for RAG-based question answering."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.rag_agent import RAGAgent
from app.schemas.agent import RAGResponse

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for chatbot operations using RAG agent."""

    async def generate_rag_response(
        self,
        user_message: str,
        project_id: UUID,
        conversation_id: UUID,
        llm_provider_id: UUID,
        db: AsyncSession,
        top_k: int = 5,
    ) -> RAGResponse:
        """Generate RAG response using agent framework.

        Args:
            user_message: User's question or query
            project_id: Project UUID to search within
            conversation_id: Conversation UUID for context
            llm_provider_id: LLM provider UUID to use
            db: Database session
            top_k: Number of chunks to retrieve (default 5)

        Returns:
            RAGResponse with generated text and source attribution

        Raises:
            ValueError: If LLM provider not found
            ConnectionError: If Ollama or LLM service unavailable
        """
        logger.info(
            f"Generating RAG response for project {project_id}, " f"conversation {conversation_id}"
        )

        try:
            # Instantiate RAG agent
            agent = RAGAgent(
                project_id=project_id,
                conversation_id=conversation_id,
                llm_provider_id=llm_provider_id,
                top_k=top_k,
            )

            # Process query through agent
            response = await agent.process_query(user_message, db)

            logger.info(
                f"RAG response generated: {len(response.response_text)} chars, "
                f"{len(response.sources)} sources"
            )

            return response

        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise
        except ConnectionError as e:
            logger.error(f"Service connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating RAG response: {e}", exc_info=True)
            raise
