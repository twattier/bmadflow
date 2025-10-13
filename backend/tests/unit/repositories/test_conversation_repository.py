"""Unit tests for ConversationRepository."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository


@pytest.mark.asyncio
async def test_create_conversation():
    """Test creating a conversation."""
    # Arrange
    mock_db = AsyncMock()
    repo = ConversationRepository()

    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    title = "Test Conversation"

    # Mock conversation ID for refresh
    conversation_id = uuid.uuid4()

    async def mock_refresh(obj):
        obj.id = conversation_id

    mock_db.refresh = mock_refresh

    # Act
    conversation = await repo.create(mock_db, project_id, llm_provider_id, title)

    # Assert
    assert conversation.project_id == project_id
    assert conversation.llm_provider_id == llm_provider_id
    assert conversation.title == title
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_with_messages():
    """Test retrieving conversation with eager-loaded messages."""
    # Arrange
    mock_db = AsyncMock()
    repo = ConversationRepository()

    conversation_id = uuid.uuid4()

    # Mock conversation with messages
    mock_conversation = MagicMock()
    mock_conversation.id = conversation_id
    mock_conversation.messages = [MagicMock(role="user"), MagicMock(role="assistant")]

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_conversation
    mock_db.execute.return_value = mock_result

    # Act
    conversation = await repo.get_by_id(mock_db, conversation_id)

    # Assert
    assert conversation.id == conversation_id
    assert len(conversation.messages) == 2
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found():
    """Test retrieving non-existent conversation returns None."""
    # Arrange
    mock_db = AsyncMock()
    repo = ConversationRepository()

    conversation_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    conversation = await repo.get_by_id(mock_db, conversation_id)

    # Assert
    assert conversation is None


@pytest.mark.asyncio
async def test_list_by_project_ordered_by_updated_at():
    """Test listing conversations ordered by updated_at DESC with limit."""
    # Arrange
    mock_db = AsyncMock()
    repo = ConversationRepository()

    project_id = uuid.uuid4()

    # Mock 3 conversations
    mock_conversations = [
        MagicMock(id=uuid.uuid4(), updated_at=datetime(2025, 1, 3)),
        MagicMock(id=uuid.uuid4(), updated_at=datetime(2025, 1, 2)),
        MagicMock(id=uuid.uuid4(), updated_at=datetime(2025, 1, 1)),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_conversations
    mock_db.execute.return_value = mock_result

    # Act
    conversations = await repo.list_by_project(mock_db, project_id, limit=10)

    # Assert
    assert len(conversations) == 3
    assert conversations[0].updated_at > conversations[1].updated_at
    assert conversations[1].updated_at > conversations[2].updated_at
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_delete_conversation():
    """Test deleting a conversation."""
    # Arrange
    mock_db = AsyncMock()
    repo = ConversationRepository()

    conversation_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute.return_value = mock_result

    # Act
    deleted = await repo.delete(mock_db, conversation_id)

    # Assert
    assert deleted is True
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_nonexistent_conversation():
    """Test deleting non-existent conversation returns False."""
    # Arrange
    mock_db = AsyncMock()
    repo = ConversationRepository()

    conversation_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_db.execute.return_value = mock_result

    # Act
    deleted = await repo.delete(mock_db, conversation_id)

    # Assert
    assert deleted is False


@pytest.mark.asyncio
async def test_update_timestamp():
    """Test updating conversation timestamp."""
    # Arrange
    mock_db = AsyncMock()
    repo = ConversationRepository()

    conversation_id = uuid.uuid4()

    # Act
    await repo.update_timestamp(mock_db, conversation_id)

    # Assert
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
