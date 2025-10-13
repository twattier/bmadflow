"""Unit tests for MessageService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.agent import RAGResponse, SourceAttribution
from app.services.chatbot_service import ChatbotService
from app.services.message_service import MessageService


@pytest.fixture
def mock_message_repo():
    """Create mock message repository."""
    return AsyncMock(spec=MessageRepository)


@pytest.fixture
def mock_conversation_repo():
    """Create mock conversation repository."""
    return AsyncMock(spec=ConversationRepository)


@pytest.fixture
def mock_chatbot_service():
    """Create mock chatbot service."""
    return AsyncMock(spec=ChatbotService)


@pytest.fixture
def message_service(mock_message_repo, mock_conversation_repo, mock_chatbot_service):
    """Create message service with mocked dependencies."""
    return MessageService(
        message_repo=mock_message_repo,
        conversation_repo=mock_conversation_repo,
        chatbot_service=mock_chatbot_service,
    )


@pytest.mark.asyncio
async def test_send_message_success(
    message_service, mock_message_repo, mock_conversation_repo, mock_chatbot_service
):
    """Test successful message sending with RAG workflow."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()
    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    user_content = "What is RAG?"

    # Mock conversation
    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = conversation_id
    mock_conversation.project_id = project_id
    mock_conversation.llm_provider_id = llm_provider_id
    mock_conversation_repo.get_by_id.return_value = mock_conversation

    # Mock user message
    user_message_id = uuid.uuid4()
    mock_user_message = MagicMock(spec=Message)
    mock_user_message.id = user_message_id
    mock_user_message.conversation_id = conversation_id
    mock_user_message.role = "user"
    mock_user_message.content = user_content
    mock_user_message.sources = None
    mock_user_message.created_at = MagicMock()
    mock_message_repo.create.side_effect = [mock_user_message, None]  # First call user, second assistant

    # Mock RAG response
    source_doc_id = uuid.uuid4()
    rag_sources = [
        SourceAttribution(
            document_id=source_doc_id,
            file_path="docs/rag.md",
            header_anchor="#what-is-rag",
            similarity_score=0.92,
        )
    ]
    rag_response = RAGResponse(
        response_text="RAG stands for Retrieval-Augmented Generation...", sources=rag_sources
    )
    mock_chatbot_service.generate_rag_response.return_value = rag_response

    # Mock assistant message
    assistant_message_id = uuid.uuid4()
    mock_assistant_message = MagicMock(spec=Message)
    mock_assistant_message.id = assistant_message_id
    mock_assistant_message.conversation_id = conversation_id
    mock_assistant_message.role = "assistant"
    mock_assistant_message.content = rag_response.response_text
    mock_assistant_message.sources = [
        {
            "document_id": str(source_doc_id),
            "file_path": "docs/rag.md",
            "header_anchor": "#what-is-rag",
            "similarity_score": 0.92,
        }
    ]
    mock_assistant_message.created_at = MagicMock()

    # Update create mock to return correct messages
    mock_message_repo.create.side_effect = [mock_user_message, mock_assistant_message]

    # Act
    result = await message_service.send_message(mock_db, conversation_id, user_content)

    # Assert
    assert result.user_message.id == user_message_id
    assert result.user_message.role == "user"
    assert result.user_message.content == user_content
    assert result.assistant_message.id == assistant_message_id
    assert result.assistant_message.role == "assistant"
    assert result.assistant_message.content == rag_response.response_text
    assert len(result.assistant_message.sources) == 1
    assert result.assistant_message.sources[0]["document_id"] == str(source_doc_id)

    # Verify calls
    mock_conversation_repo.get_by_id.assert_called_once_with(mock_db, conversation_id)
    assert mock_message_repo.create.call_count == 2

    # Verify user message creation
    user_call = mock_message_repo.create.call_args_list[0]
    assert user_call.kwargs["conversation_id"] == conversation_id
    assert user_call.kwargs["role"] == "user"
    assert user_call.kwargs["content"] == user_content
    assert user_call.kwargs["sources"] is None

    # Verify RAG call
    mock_chatbot_service.generate_rag_response.assert_called_once_with(
        user_message=user_content,
        project_id=project_id,
        conversation_id=conversation_id,
        llm_provider_id=llm_provider_id,
        db=mock_db,
    )

    # Verify assistant message creation
    assistant_call = mock_message_repo.create.call_args_list[1]
    assert assistant_call.kwargs["conversation_id"] == conversation_id
    assert assistant_call.kwargs["role"] == "assistant"
    assert assistant_call.kwargs["content"] == rag_response.response_text
    assert len(assistant_call.kwargs["sources"]) == 1

    # Verify timestamp update
    mock_conversation_repo.update_timestamp.assert_called_once_with(mock_db, conversation_id)


@pytest.mark.asyncio
async def test_send_message_conversation_not_found(
    message_service, mock_conversation_repo
):
    """Test send message when conversation does not exist."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()
    user_content = "Test message"

    mock_conversation_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await message_service.send_message(mock_db, conversation_id, user_content)

    assert exc_info.value.status_code == 404
    assert str(conversation_id) in exc_info.value.detail


@pytest.mark.asyncio
async def test_send_message_rag_failure(
    message_service, mock_message_repo, mock_conversation_repo, mock_chatbot_service
):
    """Test send message when RAG agent fails."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()
    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    user_content = "Test question"

    # Mock conversation
    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = conversation_id
    mock_conversation.project_id = project_id
    mock_conversation.llm_provider_id = llm_provider_id
    mock_conversation_repo.get_by_id.return_value = mock_conversation

    # Mock user message creation
    mock_user_message = MagicMock(spec=Message)
    mock_user_message.id = uuid.uuid4()
    mock_message_repo.create.return_value = mock_user_message

    # Mock RAG failure
    mock_chatbot_service.generate_rag_response.side_effect = Exception("LLM API error")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await message_service.send_message(mock_db, conversation_id, user_content)

    assert exc_info.value.status_code == 500
    assert "Failed to generate AI response" in exc_info.value.detail


@pytest.mark.asyncio
async def test_send_message_rag_http_exception_propagated(
    message_service, mock_message_repo, mock_conversation_repo, mock_chatbot_service
):
    """Test send message when RAG raises HTTPException (should propagate)."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()
    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    user_content = "Test question"

    # Mock conversation
    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = conversation_id
    mock_conversation.project_id = project_id
    mock_conversation.llm_provider_id = llm_provider_id
    mock_conversation_repo.get_by_id.return_value = mock_conversation

    # Mock user message creation
    mock_user_message = MagicMock(spec=Message)
    mock_user_message.id = uuid.uuid4()
    mock_message_repo.create.return_value = mock_user_message

    # Mock RAG HTTPException
    original_exception = HTTPException(status_code=503, detail="LLM service unavailable")
    mock_chatbot_service.generate_rag_response.side_effect = original_exception

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await message_service.send_message(mock_db, conversation_id, user_content)

    # Should propagate the original HTTPException, not wrap it
    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "LLM service unavailable"


@pytest.mark.asyncio
async def test_send_message_with_empty_sources(
    message_service, mock_message_repo, mock_conversation_repo, mock_chatbot_service
):
    """Test send message when RAG returns empty sources list."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()
    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    user_content = "General question"

    # Mock conversation
    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = conversation_id
    mock_conversation.project_id = project_id
    mock_conversation.llm_provider_id = llm_provider_id
    mock_conversation_repo.get_by_id.return_value = mock_conversation

    # Mock user message
    user_message_id = uuid.uuid4()
    mock_user_message = MagicMock(spec=Message)
    mock_user_message.id = user_message_id
    mock_user_message.conversation_id = conversation_id
    mock_user_message.role = "user"
    mock_user_message.content = user_content
    mock_user_message.sources = None
    mock_user_message.created_at = MagicMock()

    # Mock RAG response with no sources
    rag_response = RAGResponse(response_text="Generic answer without sources.", sources=[])
    mock_chatbot_service.generate_rag_response.return_value = rag_response

    # Mock assistant message
    assistant_message_id = uuid.uuid4()
    mock_assistant_message = MagicMock(spec=Message)
    mock_assistant_message.id = assistant_message_id
    mock_assistant_message.conversation_id = conversation_id
    mock_assistant_message.role = "assistant"
    mock_assistant_message.content = rag_response.response_text
    mock_assistant_message.sources = []
    mock_assistant_message.created_at = MagicMock()

    mock_message_repo.create.side_effect = [mock_user_message, mock_assistant_message]

    # Act
    result = await message_service.send_message(mock_db, conversation_id, user_content)

    # Assert
    assert result.assistant_message.sources == []
    assert len(result.assistant_message.sources) == 0

    # Verify assistant message created with empty sources array
    assistant_call = mock_message_repo.create.call_args_list[1]
    assert assistant_call.kwargs["sources"] == []


@pytest.mark.asyncio
async def test_send_message_with_multiple_sources(
    message_service, mock_message_repo, mock_conversation_repo, mock_chatbot_service
):
    """Test send message with multiple source attributions."""
    # Arrange
    mock_db = AsyncMock()
    conversation_id = uuid.uuid4()
    project_id = uuid.uuid4()
    llm_provider_id = uuid.uuid4()
    user_content = "Complex question needing multiple sources"

    # Mock conversation
    mock_conversation = MagicMock(spec=Conversation)
    mock_conversation.id = conversation_id
    mock_conversation.project_id = project_id
    mock_conversation.llm_provider_id = llm_provider_id
    mock_conversation_repo.get_by_id.return_value = mock_conversation

    # Mock user message
    user_message_id = uuid.uuid4()
    mock_user_message = MagicMock(spec=Message)
    mock_user_message.id = user_message_id
    mock_user_message.conversation_id = conversation_id
    mock_user_message.role = "user"
    mock_user_message.content = user_content
    mock_user_message.sources = None
    mock_user_message.created_at = MagicMock()

    # Mock RAG response with multiple sources
    doc_id_1 = uuid.uuid4()
    doc_id_2 = uuid.uuid4()
    doc_id_3 = uuid.uuid4()
    rag_sources = [
        SourceAttribution(
            document_id=doc_id_1,
            file_path="docs/intro.md",
            header_anchor="#overview",
            similarity_score=0.95,
        ),
        SourceAttribution(
            document_id=doc_id_2,
            file_path="docs/details.md",
            header_anchor="#implementation",
            similarity_score=0.88,
        ),
        SourceAttribution(
            document_id=doc_id_3,
            file_path="docs/examples.md",
            header_anchor=None,
            similarity_score=0.82,
        ),
    ]
    rag_response = RAGResponse(
        response_text="Answer based on multiple sources...", sources=rag_sources
    )
    mock_chatbot_service.generate_rag_response.return_value = rag_response

    # Mock assistant message
    assistant_message_id = uuid.uuid4()
    mock_assistant_message = MagicMock(spec=Message)
    mock_assistant_message.id = assistant_message_id
    mock_assistant_message.conversation_id = conversation_id
    mock_assistant_message.role = "assistant"
    mock_assistant_message.content = rag_response.response_text
    mock_assistant_message.sources = [
        {
            "document_id": str(doc_id_1),
            "file_path": "docs/intro.md",
            "header_anchor": "#overview",
            "similarity_score": 0.95,
        },
        {
            "document_id": str(doc_id_2),
            "file_path": "docs/details.md",
            "header_anchor": "#implementation",
            "similarity_score": 0.88,
        },
        {
            "document_id": str(doc_id_3),
            "file_path": "docs/examples.md",
            "header_anchor": None,
            "similarity_score": 0.82,
        },
    ]
    mock_assistant_message.created_at = MagicMock()

    mock_message_repo.create.side_effect = [mock_user_message, mock_assistant_message]

    # Act
    result = await message_service.send_message(mock_db, conversation_id, user_content)

    # Assert
    assert len(result.assistant_message.sources) == 3
    assert result.assistant_message.sources[0]["document_id"] == str(doc_id_1)
    assert result.assistant_message.sources[1]["document_id"] == str(doc_id_2)
    assert result.assistant_message.sources[2]["document_id"] == str(doc_id_3)
    assert result.assistant_message.sources[2]["header_anchor"] is None

    # Verify assistant message created with all sources
    assistant_call = mock_message_repo.create.call_args_list[1]
    assert len(assistant_call.kwargs["sources"]) == 3
