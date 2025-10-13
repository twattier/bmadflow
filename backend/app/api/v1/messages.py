"""API endpoints for Message operations."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message import MessageCreate, SendMessageResponse
from app.services.chatbot_service import ChatbotService
from app.services.message_service import MessageService

router = APIRouter()


def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    """Dependency injection for MessageService.

    Args:
        db: Database session from dependency

    Returns:
        MessageService instance with repositories and services
    """
    message_repo = MessageRepository()
    conversation_repo = ConversationRepository()
    chatbot_service = ChatbotService()

    return MessageService(
        message_repo=message_repo,
        conversation_repo=conversation_repo,
        chatbot_service=chatbot_service,
    )


@router.post(
    "/api/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["messages"],
    summary="Send Message",
    description="""
Send a user message and receive an AI-generated response.

**RAG Workflow**:
1. User message is stored
2. Vector search retrieves relevant documentation chunks
3. LLM generates response with context
4. Assistant message with sources is stored
5. Both messages are returned

**Performance**:
- Cloud LLMs (OpenAI, Google): <3 seconds (NFR2)
- Ollama (local): <10 seconds (NFR2)
- Vector search: <500ms (NFR4)

**Example Request**:
```json
{
  "content": "How do I configure the database?"
}
```

**Example Response**:
```json
{
  "user_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "How do I configure the database?",
    "sources": null,
    "created_at": "2025-10-13T12:00:00Z"
  },
  "assistant_message": {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "To configure the database...",
    "sources": [
      {
        "document_id": "uuid",
        "file_path": "docs/configuration.md",
        "header_anchor": "#database-setup",
        "similarity_score": 0.89
      }
    ],
    "created_at": "2025-10-13T12:00:03Z"
  }
}
```
    """,
)
async def send_message(
    conversation_id: UUID,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    service: MessageService = Depends(get_message_service),
) -> SendMessageResponse:
    """Send a message and receive AI response."""
    try:
        response = await service.send_message(
            db=db, conversation_id=conversation_id, user_content=data.content
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}",
        )
