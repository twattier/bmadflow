"""Unit tests for MessageRepository."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.message_repository import MessageRepository


@pytest.mark.asyncio
async def test_create_user_message():
    """Test creating a user message."""
    # Arrange
    mock_db = AsyncMock()
    repo = MessageRepository()

    conversation_id = uuid.uuid4()
    role = "user"
    content = "Test question"

    # Mock message ID for refresh
    message_id = uuid.uuid4()

    async def mock_refresh(obj):
        obj.id = message_id

    mock_db.refresh = mock_refresh

    # Act
    message = await repo.create(mock_db, conversation_id, role, content, sources=None)

    # Assert
    assert message.conversation_id == conversation_id
    assert message.role == role
    assert message.content == content
    assert message.sources is None
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_assistant_message_with_sources():
    """Test creating assistant message with sources."""
    # Arrange
    mock_db = AsyncMock()
    repo = MessageRepository()

    conversation_id = uuid.uuid4()
    role = "assistant"
    content = "Test answer"
    sources = [
        {
            "document_id": str(uuid.uuid4()),
            "file_path": "docs/test.md",
            "header_anchor": "#test",
            "similarity_score": 0.95,
        }
    ]

    message_id = uuid.uuid4()

    async def mock_refresh(obj):
        obj.id = message_id

    mock_db.refresh = mock_refresh

    # Act
    message = await repo.create(mock_db, conversation_id, role, content, sources=sources)

    # Assert
    assert message.role == role
    assert message.content == content
    assert message.sources == sources


@pytest.mark.asyncio
async def test_create_message_invalid_role():
    """Test creating message with invalid role raises ValueError."""
    # Arrange
    mock_db = AsyncMock()
    repo = MessageRepository()

    conversation_id = uuid.uuid4()
    invalid_role = "invalid"
    content = "Test"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid role"):
        await repo.create(mock_db, conversation_id, invalid_role, content)


@pytest.mark.asyncio
async def test_list_by_conversation_ordered():
    """Test listing messages ordered by created_at ASC."""
    # Arrange
    mock_db = AsyncMock()
    repo = MessageRepository()

    conversation_id = uuid.uuid4()

    # Mock messages in chronological order
    mock_messages = [
        MagicMock(role="user", content="Question 1"),
        MagicMock(role="assistant", content="Answer 1"),
        MagicMock(role="user", content="Question 2"),
        MagicMock(role="assistant", content="Answer 2"),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_messages
    mock_db.execute.return_value = mock_result

    # Act
    messages = await repo.list_by_conversation(mock_db, conversation_id)

    # Assert
    assert len(messages) == 4
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    mock_db.execute.assert_called_once()
