"""Unit tests for VectorSearchTool."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.agents.tools.vector_search import ChunkResult, VectorSearchTool
from app.models.chunk import Chunk


@pytest.fixture
def project_id():
    """Sample project ID."""
    return uuid4()


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_chunks():
    """Sample chunk results from database."""
    doc_id = uuid4()
    chunk1 = MagicMock(spec=Chunk)
    chunk1.id = uuid4()
    chunk1.document_id = doc_id
    chunk1.chunk_text = "This is a sample chunk about goals."
    chunk1.header_anchor = "goals"
    chunk1.chunk_index = 0
    chunk1.metadata = {"file_path": "docs/prd.md"}

    chunk2 = MagicMock(spec=Chunk)
    chunk2.id = uuid4()
    chunk2.document_id = doc_id
    chunk2.chunk_text = "This is another chunk about architecture."
    chunk2.header_anchor = None
    chunk2.chunk_index = 1
    chunk2.metadata = {"file_path": "docs/architecture.md"}

    return [(chunk1, 0.85), (chunk2, 0.72)]


@pytest.mark.asyncio
async def test_vector_search_tool_execute_success(project_id, mock_db, sample_chunks):
    """Test VectorSearchTool.execute() returns ChunkResult list."""
    # Arrange
    tool = VectorSearchTool(query="What are the goals?", top_k=5)

    with (
        patch("app.agents.tools.vector_search.EmbeddingService") as mock_embed_service,
        patch("app.agents.tools.vector_search.ChunkRepository") as mock_chunk_repo,
    ):

        # Mock embedding service
        mock_embed = AsyncMock()
        mock_embed.generate_embedding.return_value = [0.1] * 768
        mock_embed_service.return_value = mock_embed

        # Mock chunk repository
        mock_repo = AsyncMock()
        mock_repo.similarity_search.return_value = sample_chunks
        mock_chunk_repo.return_value = mock_repo

        # Act
        results = await tool.execute(project_id, mock_db)

        # Assert
        assert len(results) == 2
        assert isinstance(results[0], ChunkResult)
        assert results[0].chunk_text == "This is a sample chunk about goals."
        assert results[0].header_anchor == "goals"
        assert results[0].similarity_score == 0.85
        assert results[0].file_path == "docs/prd.md"
        assert results[1].header_anchor is None

        # Verify service calls
        mock_embed.generate_embedding.assert_called_once_with("What are the goals?")
        mock_repo.similarity_search.assert_called_once()


@pytest.mark.asyncio
async def test_vector_search_tool_with_similarity_threshold(project_id, mock_db, sample_chunks):
    """Test VectorSearchTool filters by similarity threshold."""
    # Arrange
    tool = VectorSearchTool(query="What are the goals?", top_k=5, similarity_threshold=0.8)

    with (
        patch("app.agents.tools.vector_search.EmbeddingService") as mock_embed_service,
        patch("app.agents.tools.vector_search.ChunkRepository") as mock_chunk_repo,
    ):

        mock_embed = AsyncMock()
        mock_embed.generate_embedding.return_value = [0.1] * 768
        mock_embed_service.return_value = mock_embed

        mock_repo = AsyncMock()
        mock_repo.similarity_search.return_value = sample_chunks
        mock_chunk_repo.return_value = mock_repo

        # Act
        results = await tool.execute(project_id, mock_db)

        # Assert - only chunk with similarity >= 0.8 should be returned
        assert len(results) == 1
        assert results[0].similarity_score == 0.85


@pytest.mark.asyncio
async def test_vector_search_tool_no_results(project_id, mock_db):
    """Test VectorSearchTool returns empty list when no results."""
    # Arrange
    tool = VectorSearchTool(query="nonexistent query", top_k=5)

    with (
        patch("app.agents.tools.vector_search.EmbeddingService") as mock_embed_service,
        patch("app.agents.tools.vector_search.ChunkRepository") as mock_chunk_repo,
    ):

        mock_embed = AsyncMock()
        mock_embed.generate_embedding.return_value = [0.1] * 768
        mock_embed_service.return_value = mock_embed

        mock_repo = AsyncMock()
        mock_repo.similarity_search.return_value = []
        mock_chunk_repo.return_value = mock_repo

        # Act
        results = await tool.execute(project_id, mock_db)

        # Assert
        assert results == []


def test_vector_search_tool_field_validation():
    """Test VectorSearchTool field validation."""
    # Valid tool
    tool = VectorSearchTool(query="test", top_k=10)
    assert tool.query == "test"
    assert tool.top_k == 10

    # Invalid top_k (too high)
    with pytest.raises(ValueError):
        VectorSearchTool(query="test", top_k=25)

    # Invalid top_k (too low)
    with pytest.raises(ValueError):
        VectorSearchTool(query="test", top_k=0)

    # Empty query
    with pytest.raises(ValueError):
        VectorSearchTool(query="", top_k=5)
