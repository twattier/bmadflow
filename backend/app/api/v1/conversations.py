"""API endpoints for Conversation management."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
)
from app.services.conversation_service import ConversationService

router = APIRouter()


def get_conversation_service(db: AsyncSession = Depends(get_db)) -> ConversationService:
    """Dependency injection for ConversationService.

    Args:
        db: Database session from dependency

    Returns:
        ConversationService instance with repository
    """
    conversation_repo = ConversationRepository()
    return ConversationService(conversation_repo)


@router.post(
    "/api/projects/{project_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["conversations"],
    summary="Create Conversation",
    description="""
Create a new conversation for a project.

**Title Auto-generation**: If title is not provided, it will be generated from the first user message.

**Example**:
```json
{
  "llm_provider_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Architecture Questions"
}
```
    """,
)
async def create_conversation(
    project_id: UUID,
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    """Create a new conversation."""
    # Generate title if not provided
    title = data.title or "New Conversation"

    try:
        conversation = await service.create_conversation(
            db=db,
            project_id=project_id,
            llm_provider_id=data.llm_provider_id,
            title=title,
        )
        return ConversationResponse.model_validate(conversation)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create conversation: {str(e)}",
        )


@router.get(
    "/api/projects/{project_id}/conversations",
    response_model=List[ConversationResponse],
    tags=["conversations"],
    summary="List Conversations",
    description="""
List recent conversations for a project.

Returns the last 10 conversations ordered by most recently updated (most recent first).
    """,
)
async def list_conversations(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
) -> List[ConversationResponse]:
    """List recent conversations for a project."""
    conversations = await service.list_conversations(db=db, project_id=project_id)
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get(
    "/api/conversations/{conversation_id}",
    response_model=ConversationWithMessages,
    tags=["conversations"],
    summary="Get Conversation with Messages",
    description="""
Retrieve a conversation with all its messages.

Messages are ordered chronologically (oldest to newest).
    """,
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationWithMessages:
    """Get a conversation with all messages."""
    try:
        conversation = await service.get_conversation(db=db, conversation_id=conversation_id)
        return ConversationWithMessages.model_validate(conversation)
    except HTTPException:
        raise


@router.delete(
    "/api/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["conversations"],
    summary="Delete Conversation",
    description="""
Delete a conversation and all its messages.

**Cascade Delete**: All messages associated with this conversation will be deleted automatically.
    """,
)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
) -> None:
    """Delete a conversation."""
    try:
        await service.delete_conversation(db=db, conversation_id=conversation_id)
    except HTTPException:
        raise
