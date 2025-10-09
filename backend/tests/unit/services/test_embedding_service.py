"""Unit tests for EmbeddingService."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.embedding_service import EmbeddingService


@pytest.fixture
def embedding_service():
    """Create EmbeddingService instance for testing."""
    return EmbeddingService(ollama_endpoint="http://localhost:11434", batch_size=10)


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_generate_embedding_success(mock_ollama, embedding_service):
    """Test successful embedding generation with correct dimensions."""
    # Arrange
    mock_ollama.embeddings = MagicMock(return_value={"embedding": [0.1] * 768})

    # Act
    embedding = await embedding_service.generate_embedding("test text")

    # Assert
    assert len(embedding) == 768
    assert isinstance(embedding, list)
    assert all(isinstance(x, float) for x in embedding)
    mock_ollama.embeddings.assert_called_once_with(
        model="nomic-embed-text",
        prompt="test text",
    )


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_generate_embedding_invalid_response(mock_ollama, embedding_service):
    """Test embedding generation with wrong dimension raises ValueError."""
    # Arrange - return 512 dims instead of 768
    mock_ollama.embeddings = MagicMock(return_value={"embedding": [0.1] * 512})

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid embedding dimension: expected 768, got 512"):
        await embedding_service.generate_embedding("test text")


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_generate_embeddings_batch(mock_ollama, embedding_service):
    """Test batch embedding generation processes all texts."""
    # Arrange
    texts = ["text1", "text2", "text3", "text4", "text5"]
    mock_ollama.embeddings = MagicMock(return_value={"embedding": [0.1] * 768})

    # Act
    embeddings = await embedding_service.generate_embeddings_batch(texts)

    # Assert
    assert len(embeddings) == 5
    assert all(len(emb) == 768 for emb in embeddings)
    assert mock_ollama.embeddings.call_count == 5


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_retry_on_transient_error(mock_ollama, embedding_service):
    """Test retry mechanism on transient connection errors."""
    # Arrange - fail twice, then succeed
    mock_ollama.embeddings = MagicMock(
        side_effect=[
            ConnectionError("Temporary failure"),
            ConnectionError("Temporary failure"),
            {"embedding": [0.1] * 768},
        ]
    )

    # Act
    embedding = await embedding_service.generate_embedding("test text")

    # Assert
    assert len(embedding) == 768
    assert mock_ollama.embeddings.call_count == 3


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_max_retries_exceeded(mock_ollama, embedding_service):
    """Test that max retries (3) raises final error."""
    # Arrange - always fail
    mock_ollama.embeddings = MagicMock(side_effect=ConnectionError("Persistent failure"))

    # Act & Assert
    with pytest.raises(ConnectionError):
        await embedding_service.generate_embedding("test text")

    # Should retry 3 times
    assert mock_ollama.embeddings.call_count == 3


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_validate_connection_success(mock_ollama, embedding_service):
    """Test successful Ollama connection validation."""
    # Arrange
    mock_ollama.list = MagicMock(return_value={"models": []})

    # Act
    await embedding_service.validate_connection()

    # Assert
    mock_ollama.list.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_validate_connection_failure(mock_ollama, embedding_service):
    """Test connection validation raises ConnectionError when Ollama unavailable."""
    # Arrange
    mock_ollama.list = MagicMock(side_effect=Exception("Connection refused"))

    # Act & Assert
    with pytest.raises(
        ConnectionError,
        match="Ollama service not available at http://localhost:11434",
    ):
        await embedding_service.validate_connection()


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_validate_model_success(mock_ollama, embedding_service):
    """Test successful model validation when model exists."""
    # Arrange
    mock_ollama.list = MagicMock(
        return_value={
            "models": [
                {"name": "nomic-embed-text:latest"},
                {"name": "llama2:latest"},
            ]
        }
    )

    # Act
    await embedding_service.validate_model("nomic-embed-text")

    # Assert
    mock_ollama.list.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_validate_model_missing(mock_ollama, embedding_service):
    """Test model validation raises ValueError when model not found."""
    # Arrange
    mock_ollama.list = MagicMock(
        return_value={
            "models": [
                {"name": "llama2:latest"},
            ]
        }
    )

    # Act & Assert
    with pytest.raises(
        ValueError,
        match="Model 'nomic-embed-text' not found in Ollama. Run: ollama pull nomic-embed-text",
    ):
        await embedding_service.validate_model("nomic-embed-text")


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_batch_processing_with_multiple_batches(mock_ollama, embedding_service):
    """Test batch processing splits large input into multiple batches."""
    # Arrange - 25 texts with batch size 10 = 3 batches
    texts = [f"text{i}" for i in range(25)]
    mock_ollama.embeddings = MagicMock(return_value={"embedding": [0.1] * 768})

    # Act
    embeddings = await embedding_service.generate_embeddings_batch(texts)

    # Assert
    assert len(embeddings) == 25
    assert mock_ollama.embeddings.call_count == 25


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_embedding_with_empty_text(mock_ollama, embedding_service):
    """Test embedding generation with empty string."""
    # Arrange
    mock_ollama.embeddings = MagicMock(return_value={"embedding": [0.0] * 768})

    # Act
    embedding = await embedding_service.generate_embedding("")

    # Assert
    assert len(embedding) == 768
    mock_ollama.embeddings.assert_called_once_with(
        model="nomic-embed-text",
        prompt="",
    )


@pytest.mark.asyncio
@patch("app.services.embedding_service.ollama")
async def test_timeout_error_triggers_retry(mock_ollama, embedding_service):
    """Test that TimeoutError triggers retry mechanism."""
    # Arrange - timeout once, then succeed
    mock_ollama.embeddings = MagicMock(
        side_effect=[
            TimeoutError("Request timeout"),
            {"embedding": [0.1] * 768},
        ]
    )

    # Act
    embedding = await embedding_service.generate_embedding("test text")

    # Assert
    assert len(embedding) == 768
    assert mock_ollama.embeddings.call_count == 2
