"""Integration tests for Messages API."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.main import app
from app.models.conversation import Conversation
from app.models.llm_provider import LLMProvider
from app.models.message import Message
from app.models.project import Project
from app.schemas.agent import RAGResponse, SourceAttribution


@pytest.mark.asyncio
async def test_send_message_success(db_session: AsyncSession):
    """Test successful message sending with mocked RAG response."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange: Create project, provider, and conversation
        project = Project(id=uuid.uuid4(), name="Test Project", description="Test")
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)

        conversation = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Test Conversation",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Mock RAG response
        doc_id = uuid.uuid4()
        mock_rag_response = RAGResponse(
            response_text="RAG stands for Retrieval-Augmented Generation. It combines retrieval with generation.",
            sources=[
                SourceAttribution(
                    document_id=doc_id,
                    file_path="docs/rag.md",
                    header_anchor="#what-is-rag",
                    similarity_score=0.95,
                )
            ],
        )

        # Act: Send message with mocked chatbot service
        with patch(
            "app.services.chatbot_service.ChatbotService.generate_rag_response",
            new_callable=AsyncMock,
            return_value=mock_rag_response,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    f"/api/conversations/{conversation.id}/messages",
                    json={"content": "What is RAG?"},
                )

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Verify user message
        assert data["user_message"]["role"] == "user"
        assert data["user_message"]["content"] == "What is RAG?"
        assert data["user_message"]["sources"] is None
        assert data["user_message"]["conversation_id"] == str(conversation.id)

        # Verify assistant message
        assert data["assistant_message"]["role"] == "assistant"
        assert "Retrieval-Augmented Generation" in data["assistant_message"]["content"]
        assert len(data["assistant_message"]["sources"]) == 1
        assert data["assistant_message"]["sources"][0]["file_path"] == "docs/rag.md"
        assert data["assistant_message"]["sources"][0]["header_anchor"] == "#what-is-rag"
        assert data["assistant_message"]["sources"][0]["similarity_score"] == 0.95


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_with_multiple_sources(db_session: AsyncSession):
    """Test message with multiple source attributions."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(id=uuid.uuid4(), name="Test Project", description="Test")
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)

        conversation = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Test Conversation",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Mock RAG response with multiple sources
        doc_id_1 = uuid.uuid4()
        doc_id_2 = uuid.uuid4()
        doc_id_3 = uuid.uuid4()
        mock_rag_response = RAGResponse(
            response_text="Here's a comprehensive answer based on multiple documents...",
            sources=[
                SourceAttribution(
                    document_id=doc_id_1,
                    file_path="docs/intro.md",
                    header_anchor="#overview",
                    similarity_score=0.92,
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
                    similarity_score=0.85,
                ),
            ],
        )

        # Act
        with patch(
            "app.services.chatbot_service.ChatbotService.generate_rag_response",
            new_callable=AsyncMock,
            return_value=mock_rag_response,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    f"/api/conversations/{conversation.id}/messages",
                    json={"content": "Tell me about the system"},
                )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert len(data["assistant_message"]["sources"]) == 3
        assert data["assistant_message"]["sources"][0]["file_path"] == "docs/intro.md"
        assert data["assistant_message"]["sources"][1]["file_path"] == "docs/details.md"
        assert data["assistant_message"]["sources"][2]["file_path"] == "docs/examples.md"
        assert data["assistant_message"]["sources"][2]["header_anchor"] is None


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_with_empty_sources(db_session: AsyncSession):
    """Test message when RAG returns no sources."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(id=uuid.uuid4(), name="Test Project", description="Test")
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)

        conversation = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Test Conversation",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Mock RAG response with no sources
        mock_rag_response = RAGResponse(
            response_text="I don't have specific documentation about that.",
            sources=[],
        )

        # Act
        with patch(
            "app.services.chatbot_service.ChatbotService.generate_rag_response",
            new_callable=AsyncMock,
            return_value=mock_rag_response,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    f"/api/conversations/{conversation.id}/messages",
                    json={"content": "Random question"},
                )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["assistant_message"]["sources"] == []
        assert len(data["assistant_message"]["sources"]) == 0


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_conversation_not_found(db_session: AsyncSession):
    """Test sending message to non-existent conversation."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        fake_conversation_id = uuid.uuid4()

        # Act
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/conversations/{fake_conversation_id}/messages",
                json={"content": "Test message"},
            )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_creates_database_records(db_session: AsyncSession):
    """Test that sending message creates both user and assistant messages in database."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(id=uuid.uuid4(), name="Test Project", description="Test")
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)

        conversation = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Test Conversation",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Mock RAG response
        mock_rag_response = RAGResponse(
            response_text="Test response",
            sources=[],
        )

        # Act
        with patch(
            "app.services.chatbot_service.ChatbotService.generate_rag_response",
            new_callable=AsyncMock,
            return_value=mock_rag_response,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    f"/api/conversations/{conversation.id}/messages",
                    json={"content": "Test question"},
                )

        # Assert: Verify response
        assert response.status_code == 201

        # Verify database records
        await db_session.refresh(conversation)
        result = await db_session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()

        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Test question"
        assert messages[0].sources is None

        assert messages[1].role == "assistant"
        assert messages[1].content == "Test response"
        assert messages[1].sources == []


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_updates_conversation_timestamp(db_session: AsyncSession):
    """Test that sending message updates conversation's updated_at timestamp."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(id=uuid.uuid4(), name="Test Project", description="Test")
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)

        conversation = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Test Conversation",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Get initial timestamp
        initial_updated_at = conversation.updated_at

        # Mock RAG response
        mock_rag_response = RAGResponse(
            response_text="Test response",
            sources=[],
        )

        # Act: Send message
        with patch(
            "app.services.chatbot_service.ChatbotService.generate_rag_response",
            new_callable=AsyncMock,
            return_value=mock_rag_response,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                await client.post(
                    f"/api/conversations/{conversation.id}/messages",
                    json={"content": "Test question"},
                )

        # Assert: Verify timestamp updated
        await db_session.refresh(conversation)
        assert conversation.updated_at >= initial_updated_at


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_empty_content_validation(db_session: AsyncSession):
    """Test that empty message content is rejected."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(id=uuid.uuid4(), name="Test Project", description="Test")
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)

        conversation = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Test Conversation",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Act: Send message with empty content
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/conversations/{conversation.id}/messages",
                json={"content": ""},
            )

        # Assert: Should fail validation
        assert response.status_code == 422  # Unprocessable Entity


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_sources_stored_as_jsonb(db_session: AsyncSession):
    """Test that sources are correctly stored as JSONB in database."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(id=uuid.uuid4(), name="Test Project", description="Test")
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)

        conversation = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Test Conversation",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Mock RAG response
        doc_id = uuid.uuid4()
        mock_rag_response = RAGResponse(
            response_text="Test response",
            sources=[
                SourceAttribution(
                    document_id=doc_id,
                    file_path="docs/test.md",
                    header_anchor="#section",
                    similarity_score=0.87,
                )
            ],
        )

        # Act
        with patch(
            "app.services.chatbot_service.ChatbotService.generate_rag_response",
            new_callable=AsyncMock,
            return_value=mock_rag_response,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                await client.post(
                    f"/api/conversations/{conversation.id}/messages",
                    json={"content": "Test question"},
                )

        # Assert: Verify JSONB structure in database
        result = await db_session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .where(Message.role == "assistant")
        )
        assistant_message = result.scalar_one()

        assert assistant_message.sources is not None
        assert isinstance(assistant_message.sources, list)
        assert len(assistant_message.sources) == 1
        assert assistant_message.sources[0]["document_id"] == str(doc_id)
        assert assistant_message.sources[0]["file_path"] == "docs/test.md"
        assert assistant_message.sources[0]["header_anchor"] == "#section"
        assert assistant_message.sources[0]["similarity_score"] == 0.87

    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()
