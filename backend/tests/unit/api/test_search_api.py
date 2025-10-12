"""Unit tests for vector similarity search API endpoint."""

import uuid
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_chunk_repository, get_embedding_service
from app.main import app
from app.models.chunk import Chunk


@pytest.fixture
def mock_embedding_service() -> Mock:
    """Mock EmbeddingService for unit tests.

    Returns:
        Mock EmbeddingService with generate_embedding method
    """
    service = Mock()
    service.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    return service


@pytest.fixture
def mock_chunk_repository() -> Mock:
    """Mock ChunkRepository for unit tests.

    Returns:
        Mock ChunkRepository with similarity_search method
    """
    repo = Mock()

    # Create mock chunks
    chunk1 = Mock(spec=Chunk)
    chunk1.id = uuid.uuid4()
    chunk1.document_id = uuid.uuid4()
    chunk1.chunk_text = "The RAG pipeline integrates Docling for document processing..."
    chunk1.header_anchor = "rag-pipeline"
    chunk1.chunk_metadata = {
        "file_path": "docs/architecture.md",
        "file_name": "architecture.md",
        "file_type": "md",
    }

    chunk2 = Mock(spec=Chunk)
    chunk2.id = uuid.uuid4()
    chunk2.document_id = uuid.uuid4()
    chunk2.chunk_text = "Vector search uses pgvector with HNSW indexing..."
    chunk2.header_anchor = "vector-search"
    chunk2.chunk_metadata = {
        "file_path": "docs/backend.md",
        "file_name": "backend.md",
        "file_type": "md",
    }

    # Mock similarity_search to return list of (chunk, score) tuples
    repo.similarity_search = AsyncMock(return_value=[(chunk1, 0.89), (chunk2, 0.75)])
    return repo


@pytest.fixture
def test_client(mock_embedding_service: Mock, mock_chunk_repository: Mock) -> TestClient:
    """Create test client with mocked dependencies.

    Args:
        mock_embedding_service: Mocked embedding service
        mock_chunk_repository: Mocked chunk repository

    Returns:
        FastAPI test client with overridden dependencies
    """
    app.dependency_overrides[get_embedding_service] = lambda: mock_embedding_service
    app.dependency_overrides[get_chunk_repository] = lambda: mock_chunk_repository
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_endpoint_success(
    test_client: TestClient, mock_embedding_service: Mock, mock_chunk_repository: Mock
) -> None:
    """Test successful search with valid query.

    Verifies:
    - Response status 200
    - SearchResponse structure correct
    - Results contain required fields (chunk_text, similarity_score, header_anchor)
    - Embedding service called with query text
    - Repository called with correct parameters
    """
    project_id = str(uuid.uuid4())
    response = test_client.post(
        f"/api/projects/{project_id}/search",
        json={"query": "How does the RAG pipeline work?", "top_k": 5},
    )

    # Assert response status
    assert response.status_code == 200

    # Assert response structure
    data = response.json()
    assert data["query"] == "How does the RAG pipeline work?"
    assert "results" in data
    assert "total_results" in data
    assert data["total_results"] == 2

    # Assert results contain required fields
    result = data["results"][0]
    assert "chunk_id" in result
    assert "document_id" in result
    assert "chunk_text" in result
    assert "similarity_score" in result
    assert "header_anchor" in result
    assert "metadata" in result

    # Verify similarity scores are within valid range
    assert 0.0 <= result["similarity_score"] <= 1.0

    # Verify services were called correctly
    mock_embedding_service.generate_embedding.assert_called_once_with(
        "How does the RAG pipeline work?"
    )
    mock_chunk_repository.similarity_search.assert_called_once()


@pytest.mark.asyncio
async def test_search_top_k_validation(test_client: TestClient) -> None:
    """Test top_k parameter validation.

    Verifies:
    - top_k=0 returns 422 validation error
    - top_k=21 (exceeds max) returns 422 validation error
    """
    project_id = str(uuid.uuid4())

    # Test top_k=0 (below minimum)
    response = test_client.post(
        f"/api/projects/{project_id}/search",
        json={"query": "test query", "top_k": 0},
    )
    assert response.status_code == 422

    # Test top_k=21 (exceeds maximum)
    response = test_client.post(
        f"/api/projects/{project_id}/search",
        json={"query": "test query", "top_k": 21},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_filters_by_project(
    test_client: TestClient, mock_chunk_repository: Mock
) -> None:
    """Test that search filters results by project_id.

    Verifies:
    - Repository's similarity_search called with correct project_id
    - Project isolation is maintained
    """
    project_id = uuid.uuid4()
    response = test_client.post(
        f"/api/projects/{project_id}/search",
        json={"query": "test query", "top_k": 5},
    )

    assert response.status_code == 200

    # Verify repository was called with the correct project_id
    call_args = mock_chunk_repository.similarity_search.call_args
    assert call_args.kwargs["project_id"] == project_id


@pytest.mark.asyncio
async def test_search_empty_results(test_client: TestClient, mock_chunk_repository: Mock) -> None:
    """Test search with no matching results.

    Verifies:
    - Response has total_results=0
    - Results array is empty
    - Status code is 200 (successful but empty)
    """
    # Mock empty results
    mock_chunk_repository.similarity_search = AsyncMock(return_value=[])

    project_id = str(uuid.uuid4())
    response = test_client.post(
        f"/api/projects/{project_id}/search",
        json={"query": "nonexistent query", "top_k": 5},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total_results"] == 0
    assert data["results"] == []
    assert data["query"] == "nonexistent query"


@pytest.mark.asyncio
async def test_search_embedding_service_error(
    test_client: TestClient, mock_embedding_service: Mock
) -> None:
    """Test error handling when embedding service fails.

    Verifies:
    - ConnectionError from Ollama results in 500 status
    - Error message indicates service unavailability
    """
    # Mock embedding service failure
    mock_embedding_service.generate_embedding = AsyncMock(
        side_effect=ConnectionError("Ollama unavailable")
    )

    project_id = str(uuid.uuid4())
    response = test_client.post(
        f"/api/projects/{project_id}/search",
        json={"query": "test query", "top_k": 5},
    )

    assert response.status_code == 500
    assert "unavailable" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_search_empty_query_validation(test_client: TestClient) -> None:
    """Test that empty query string is rejected.

    Verifies:
    - Empty query returns 422 validation error
    """
    project_id = str(uuid.uuid4())
    response = test_client.post(
        f"/api/projects/{project_id}/search",
        json={"query": "", "top_k": 5},
    )

    assert response.status_code == 422
