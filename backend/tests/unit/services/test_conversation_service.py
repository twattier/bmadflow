"""Unit tests for ConversationService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.services.conversation_service import ConversationService


@pytest.fixture
def mock_conversation_repo():
    """Create mock conversation repository."""
    return AsyncMock(spec=ConversationRepository)


@pytest.fixture
def conversation_service(mock_conversation_repo):
    """Create conversation service with mocked repository."""
    return ConversationService(conversation_repo=mock_conversation_repo)


@pytest.mark.asyncio
async def test_create_conversation_success(conversation_service, mock_conversation_repo):
    """Test successful conversation creation."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    title = "Test Conversation"

    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = uuid.uuid4()
    mock_conversation.project_id = project_id
    mock_conversation.llm_provider_id = llm_provider_id
    mock_conversation.title = title

    mock_conversation_repo.create.return_value = mock_conversation

    # Act
    result = await conversation_service.create_conversation(
        mock_db, project_id, llm_provider_id, title
    )

    # Assert
    assert result.id == mock_conversation.id
    assert result.project_id == project_id
    assert result.llm_provider_id == llm_provider_id
    assert result.title == title
    mock_conversation_repo.create.assert_called_once_with(
        mock_db, project_id, llm_provider_id, title
    )


@pytest.mark.asyncio
async def test_create_conversation_repository_error(conversation_service, mock_conversation_repo):
    """Test conversation creation when repository raises exception."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    title = "Test Conversation"

    mock_conversation_repo.create.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await conversation_service.create_conversation(
            mock_db, project_id, llm_provider_id, title
        )

    assert exc_info.value.status_code == 500
    assert "Failed to create conversation" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_conversation_success(conversation_service, mock_conversation_repo):
    """Test successful conversation retrieval."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()

    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = conversation_id
    mock_conversation.messages = [MagicMock(role="user"), MagicMock(role="assistant")]

    mock_conversation_repo.get_by_id.return_value = mock_conversation

    # Act
    result = await conversation_service.get_conversation(mock_db, conversation_id)

    # Assert
    assert result.id == conversation_id
    assert len(result.messages) == 2
    mock_conversation_repo.get_by_id.assert_called_once_with(mock_db, conversation_id)


@pytest.mark.asyncio
async def test_get_conversation_not_found(conversation_service, mock_conversation_repo):
    """Test get conversation when conversation does not exist."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()

    mock_conversation_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await conversation_service.get_conversation(mock_db, conversation_id)

    assert exc_info.value.status_code == 404
    assert str(conversation_id) in exc_info.value.detail


@pytest.mark.asyncio
async def test_list_conversations_success(conversation_service, mock_conversation_repo):
    """Test successful listing of conversations."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid.uuid4()

    mock_conversations = [
        MagicMock(id=uuid.uuid4(), title="Conversation 1"),
        MagicMock(id=uuid.uuid4(), title="Conversation 2"),
        MagicMock(id=uuid.uuid4(), title="Conversation 3"),
    ]

    mock_conversation_repo.list_by_project.return_value = mock_conversations

    # Act
    result = await conversation_service.list_conversations(mock_db, project_id)

    # Assert
    assert len(result) == 3
    assert result == mock_conversations
    mock_conversation_repo.list_by_project.assert_called_once_with(mock_db, project_id)


@pytest.mark.asyncio
async def test_list_conversations_empty(conversation_service, mock_conversation_repo):
    """Test listing conversations when project has no conversations."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid.uuid4()

    mock_conversation_repo.list_by_project.return_value = []

    # Act
    result = await conversation_service.list_conversations(mock_db, project_id)

    # Assert
    assert len(result) == 0
    assert result == []


@pytest.mark.asyncio
async def test_delete_conversation_success(conversation_service, mock_conversation_repo):
    """Test successful conversation deletion."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()

    mock_conversation_repo.delete.return_value = True

    # Act
    await conversation_service.delete_conversation(mock_db, conversation_id)

    # Assert
    mock_conversation_repo.delete.assert_called_once_with(mock_db, conversation_id)


@pytest.mark.asyncio
async def test_delete_conversation_not_found(conversation_service, mock_conversation_repo):
    """Test delete conversation when conversation does not exist."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()

    mock_conversation_repo.delete.return_value = False

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await conversation_service.delete_conversation(mock_db, conversation_id)

    assert exc_info.value.status_code == 404
    assert str(conversation_id) in exc_info.value.detail
