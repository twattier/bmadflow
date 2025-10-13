"""Unit tests for RAG Agent."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.agents.rag_agent import RAGAgent
from app.agents.tools.vector_search import ChunkResult
from app.schemas.agent import RAGResponse, SourceAttribution


@pytest.fixture
def project_id():
    """Sample project ID."""
    return uuid4()


@pytest.fixture
def conversation_id():
    """Sample conversation ID."""
    return uuid4()


@pytest.fixture
def llm_provider_id():
    """Sample LLM provider ID."""
    return uuid4()


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_chunk_results():
    """Sample ChunkResult objects."""
    return [
        ChunkResult(
            chunk_id=uuid4(),
            document_id=uuid4(),
            chunk_text="The project goals are to build a documentation hub.",
            file_path="docs/prd.md",
            header_anchor="goals",
            similarity_score=0.85,
            chunk_index=0,
        ),
        ChunkResult(
            chunk_id=uuid4(),
            document_id=uuid4(),
            chunk_text="The architecture follows a monorepo structure.",
            file_path="docs/architecture.md",
            header_anchor=None,
            similarity_score=0.72,
            chunk_index=1,
        ),
    ]


@pytest.mark.asyncio
async def test_rag_agent_process_query_success(
    project_id, conversation_id, llm_provider_id, mock_db, sample_chunk_results
):
    """Test RAGAgent.process_query() returns RAGResponse with sources."""
    # Arrange
    agent = RAGAgent(
        project_id=project_id,
        conversation_id=conversation_id,
        llm_provider_id=llm_provider_id,
        top_k=5,
    )

    mock_llm_response = "The project aims to build a documentation hub with a monorepo structure."

    with (
        patch("app.agents.rag_agent.VectorSearchTool") as mock_search_tool,
        patch("app.agents.rag_agent.LLMService") as mock_llm_service,
    ):

        # Mock vector search tool
        mock_tool = AsyncMock()
        mock_tool.execute.return_value = sample_chunk_results
        mock_search_tool.return_value = mock_tool

        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_completion.return_value = mock_llm_response
        mock_llm_service.return_value = mock_llm

        # Act
        response = await agent.process_query("What are the project goals?", mock_db)

        # Assert
        assert isinstance(response, RAGResponse)
        assert response.response_text == mock_llm_response
        assert len(response.sources) == 2
        assert isinstance(response.sources[0], SourceAttribution)
        assert response.sources[0].file_path == "docs/prd.md"
        assert response.sources[0].header_anchor == "goals"
        assert response.sources[0].similarity_score == 0.85
        assert response.sources[1].header_anchor is None

        # Verify tool calls
        mock_tool.execute.assert_called_once()
        mock_llm.generate_completion.assert_called_once()


@pytest.mark.asyncio
async def test_rag_agent_process_query_no_chunks_found(
    project_id, conversation_id, llm_provider_id, mock_db
):
    """Test RAGAgent.process_query() handles no chunks found."""
    # Arrange
    agent = RAGAgent(
        project_id=project_id,
        conversation_id=conversation_id,
        llm_provider_id=llm_provider_id,
        top_k=5,
    )

    with patch("app.agents.rag_agent.VectorSearchTool") as mock_search_tool:
        # Mock vector search tool returning empty list
        mock_tool = AsyncMock()
        mock_tool.execute.return_value = []
        mock_search_tool.return_value = mock_tool

        # Act
        response = await agent.process_query("What is XYZ?", mock_db)

        # Assert
        assert isinstance(response, RAGResponse)
        assert "couldn't find any relevant information" in response.response_text.lower()
        assert len(response.sources) == 0


@pytest.mark.asyncio
async def test_rag_agent_llm_failure(
    project_id, conversation_id, llm_provider_id, mock_db, sample_chunk_results
):
    """Test RAGAgent.process_query() propagates LLM errors."""
    # Arrange
    agent = RAGAgent(
        project_id=project_id,
        conversation_id=conversation_id,
        llm_provider_id=llm_provider_id,
        top_k=5,
    )

    with (
        patch("app.agents.rag_agent.VectorSearchTool") as mock_search_tool,
        patch("app.agents.rag_agent.LLMService") as mock_llm_service,
    ):

        mock_tool = AsyncMock()
        mock_tool.execute.return_value = sample_chunk_results
        mock_search_tool.return_value = mock_tool

        # Mock LLM service raising error
        mock_llm = AsyncMock()
        mock_llm.generate_completion.side_effect = ConnectionError("LLM unavailable")
        mock_llm_service.return_value = mock_llm

        # Act & Assert
        with pytest.raises(ConnectionError):
            await agent.process_query("What are the project goals?", mock_db)


def test_rag_agent_format_context(
    project_id, conversation_id, llm_provider_id, sample_chunk_results
):
    """Test RAGAgent._format_context() formats chunks correctly."""
    # Arrange
    agent = RAGAgent(
        project_id=project_id,
        conversation_id=conversation_id,
        llm_provider_id=llm_provider_id,
    )

    # Act
    context = agent._format_context(sample_chunk_results)

    # Assert
    assert "[Source 1: prd.md#goals]" in context
    assert "[Source 2: architecture.md]" in context
    assert "The project goals are to build a documentation hub." in context
    assert "The architecture follows a monorepo structure." in context


def test_rag_agent_format_context_without_anchor(project_id, conversation_id, llm_provider_id):
    """Test RAGAgent._format_context() handles chunks without header_anchor."""
    # Arrange
    agent = RAGAgent(
        project_id=project_id,
        conversation_id=conversation_id,
        llm_provider_id=llm_provider_id,
    )

    chunks = [
        ChunkResult(
            chunk_id=uuid4(),
            document_id=uuid4(),
            chunk_text="Test content",
            file_path="docs/test.md",
            header_anchor=None,
            similarity_score=0.8,
            chunk_index=0,
        )
    ]

    # Act
    context = agent._format_context(chunks)

    # Assert
    assert "[Source 1: test.md]" in context
    assert "[Source 1: test.md#" not in context


def test_rag_agent_format_sources(
    project_id, conversation_id, llm_provider_id, sample_chunk_results
):
    """Test RAGAgent._format_sources() returns SourceAttribution list."""
    # Arrange
    agent = RAGAgent(
        project_id=project_id,
        conversation_id=conversation_id,
        llm_provider_id=llm_provider_id,
    )

    # Act
    sources = agent._format_sources(sample_chunk_results)

    # Assert
    assert len(sources) == 2
    assert all(isinstance(s, SourceAttribution) for s in sources)
    assert sources[0].file_path == "docs/prd.md"
    assert sources[0].header_anchor == "goals"
    assert sources[1].header_anchor is None
