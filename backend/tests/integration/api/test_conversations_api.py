"""Integration tests for Conversations API."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.main import app
from app.models.conversation import Conversation
from app.models.llm_provider import LLMProvider
from app.models.message import Message
from app.models.project import Project


@pytest.mark.asyncio
async def test_create_conversation_success(db_session: AsyncSession):
    """Test successful conversation creation."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange: Create project
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            description="Test project for conversations",
        )
        db_session.add(project)
        await db_session.commit()

        # Create LLM provider
        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)
        await db_session.commit()

        # Act: Create conversation
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/projects/{project.id}/conversations",
                json={
                    "llm_provider_id": str(llm_provider.id),
                    "title": "Test Conversation",
                },
            )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == str(project.id)
        assert data["llm_provider_id"] == str(llm_provider.id)
        assert data["title"] == "Test Conversation"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_conversation_without_title(db_session: AsyncSession):
    """Test conversation creation with auto-generated title."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(
            id=uuid.uuid4(),
            name="Test Project",
            description="Test",
        )
        db_session.add(project)

        llm_provider = LLMProvider(
            id=uuid.uuid4(),
            provider_name="ollama",
            model_name="llama3.2:3b",
            is_default=True,
            api_config={},
        )
        db_session.add(llm_provider)
        await db_session.commit()

        # Act
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/projects/{project.id}/conversations",
                json={"llm_provider_id": str(llm_provider.id)},
            )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Conversation"


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_list_conversations_ordered_by_updated_at(db_session: AsyncSession):
    """Test listing conversations ordered by most recently updated."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange: Create project and LLM provider
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
        await db_session.commit()

        # Create 3 conversations
        conv1 = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Conversation 1",
        )
        conv2 = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Conversation 2",
        )
        conv3 = Conversation(
            id=uuid.uuid4(),
            project_id=project.id,
            llm_provider_id=llm_provider.id,
            title="Conversation 3",
        )
        db_session.add_all([conv1, conv2, conv3])
        await db_session.commit()

        # Act: List conversations
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/projects/{project.id}/conversations")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Verify all conversations returned
        titles = {conv["title"] for conv in data}
        assert titles == {"Conversation 1", "Conversation 2", "Conversation 3"}


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_list_conversations_empty_project(db_session: AsyncSession):
    """Test listing conversations for project with no conversations."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        project = Project(id=uuid.uuid4(), name="Empty Project", description="Test")
        db_session.add(project)
        await db_session.commit()

        # Act
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/projects/{project.id}/conversations")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == []


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_conversation_with_messages(db_session: AsyncSession):
    """Test retrieving conversation with messages."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange: Create project, provider, conversation, and messages
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

        # Create messages
        msg1 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="What is RAG?",
            sources=None,
        )
        msg2 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content="RAG stands for Retrieval-Augmented Generation...",
            sources=[
                {
                    "document_id": str(uuid.uuid4()),
                    "file_path": "docs/rag.md",
                    "header_anchor": "#what-is-rag",
                    "similarity_score": 0.95,
                }
            ],
        )
        db_session.add_all([msg1, msg2])
        await db_session.commit()

        # Act
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/conversations/{conversation.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(conversation.id)
        assert data["title"] == "Test Conversation"
        assert len(data["messages"]) == 2

        # Verify message ordering and content
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][0]["content"] == "What is RAG?"
        assert data["messages"][0]["sources"] is None

        assert data["messages"][1]["role"] == "assistant"
        assert data["messages"][1]["content"] == "RAG stands for Retrieval-Augmented Generation..."
        assert len(data["messages"][1]["sources"]) == 1
        assert data["messages"][1]["sources"][0]["file_path"] == "docs/rag.md"


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_conversation_not_found(db_session: AsyncSession):
    """Test getting non-existent conversation returns 404."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        fake_conversation_id = uuid.uuid4()

        # Act
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/conversations/{fake_conversation_id}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_conversation_success(db_session: AsyncSession):
    """Test successful conversation deletion."""
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
            title="To Delete",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Act: Delete conversation
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/api/conversations/{conversation.id}")

        # Assert
        assert response.status_code == 204

        # Verify conversation no longer exists
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            get_response = await client.get(f"/api/conversations/{conversation.id}")
            assert get_response.status_code == 404


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_conversation_not_found(db_session: AsyncSession):
    """Test deleting non-existent conversation returns 404."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange
        fake_conversation_id = uuid.uuid4()

        # Act
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/api/conversations/{fake_conversation_id}")

        # Assert
        assert response.status_code == 404


    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_conversation_cascades_to_messages(db_session: AsyncSession):
    """Test deleting conversation also deletes associated messages."""
    # Override get_db dependency to use test session
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        # Arrange: Create conversation with messages
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
            title="To Delete",
        )
        db_session.add(conversation)
        await db_session.commit()

        # Create messages
        msg1 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="Test message",
        )
        msg2 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content="Test response",
        )
        db_session.add_all([msg1, msg2])
        await db_session.commit()

        # Act: Delete conversation
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/api/conversations/{conversation.id}")

        # Assert
        assert response.status_code == 204

        # Verify messages were also deleted (cascade)
        from sqlalchemy import select

        result = await db_session.execute(
            select(Message).where(Message.conversation_id == conversation.id)
        )
        messages = result.scalars().all()
        assert len(messages) == 0

    finally:
        # Clear dependency override after test
        app.dependency_overrides.clear()
