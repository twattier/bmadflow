"""Integration tests for Ollama embedding service.

These tests require:
- Ollama running at localhost:11434
- nomic-embed-text model pulled

Tests will be skipped if Ollama is not available.
"""

import time

import pytest

from app.services.embedding_service import EmbeddingService


@pytest.fixture
async def embedding_service():
    """Create embedding service instance."""
    return EmbeddingService(ollama_endpoint="http://localhost:11434")


async def is_ollama_available(embedding_service):
    """Check if Ollama is available and model is installed."""
    try:
        await embedding_service.validate_connection()
        await embedding_service.validate_model("nomic-embed-text")
        return True
    except (ConnectionError, ValueError):
        return False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_ollama_embedding(embedding_service):
    """Test real Ollama embedding generation.

    Integration test requiring:
    - Ollama running at localhost:11434
    - nomic-embed-text model pulled

    Skip if Ollama not available.
    """
    if not await is_ollama_available(embedding_service):
        pytest.skip("Ollama not available or model not installed")

    # Act
    embedding = await embedding_service.generate_embedding("test document text")

    # Assert
    assert len(embedding) == 768, f"Expected 768 dims, got {len(embedding)}"
    assert all(isinstance(x, float) for x in embedding), "All values should be floats"
    assert any(x != 0.0 for x in embedding), "Embedding should contain non-zero values"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_embedding_performance(embedding_service):
    """Test batch embedding performance with 100 chunks in <10 seconds.

    Integration test requiring:
    - Ollama running at localhost:11434
    - nomic-embed-text model pulled

    Skip if Ollama not available.
    """
    if not await is_ollama_available(embedding_service):
        pytest.skip("Ollama not available or model not installed")

    # Arrange - create 100 text chunks
    texts = [f"This is test document chunk number {i} with some content." for i in range(100)]

    # Act
    start_time = time.time()
    embeddings = await embedding_service.generate_embeddings_batch(texts)
    elapsed_time = time.time() - start_time

    # Assert
    assert len(embeddings) == 100, "Should generate 100 embeddings"
    assert all(len(emb) == 768 for emb in embeddings), "All embeddings should be 768-dim"
    assert elapsed_time < 10.0, f"Batch processing took {elapsed_time:.2f}s, expected <10s"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_connection_validation(embedding_service):
    """Test Ollama connection validation with real service."""
    # This test will pass if Ollama is running, fail if not
    try:
        await embedding_service.validate_connection()
        # If we get here, Ollama is running
        assert True
    except ConnectionError:
        # Expected if Ollama is not running
        pytest.skip("Ollama not running at localhost:11434")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_model_validation_with_real_ollama(embedding_service):
    """Test model validation with real Ollama instance."""
    if not await is_ollama_available(embedding_service):
        pytest.skip("Ollama not available")

    # Act & Assert - should not raise
    await embedding_service.validate_model("nomic-embed-text")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_model_validation_missing_model(embedding_service):
    """Test model validation fails for non-existent model."""
    if not await is_ollama_available(embedding_service):
        pytest.skip("Ollama not available")

    # Act & Assert
    with pytest.raises(ValueError, match="Model 'nonexistent-model' not found"):
        await embedding_service.validate_model("nonexistent-model")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_embedding_with_various_text_lengths(embedding_service):
    """Test embedding generation with various text lengths."""
    if not await is_ollama_available(embedding_service):
        pytest.skip("Ollama not available or model not installed")

    # Arrange - texts of different lengths
    test_cases = [
        "Short",
        "Medium length text with a few words",
        "This is a longer text that contains multiple sentences. " * 10,
        "",  # Empty text
    ]

    # Act & Assert
    for text in test_cases:
        embedding = await embedding_service.generate_embedding(text)
        assert len(embedding) == 768, f"Failed for text length {len(text)}"
        assert all(isinstance(x, float) for x in embedding)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_size_configuration():
    """Test that batch size configuration works correctly."""
    # Create custom service
    custom_service = EmbeddingService(batch_size=5)

    if not await is_ollama_available(custom_service):
        pytest.skip("Ollama not available or model not installed")

    # Arrange - custom batch size
    custom_service = EmbeddingService(batch_size=5)
    texts = [f"text {i}" for i in range(12)]  # 12 texts with batch size 5 = 3 batches

    # Act
    embeddings = await custom_service.generate_embeddings_batch(texts)

    # Assert
    assert len(embeddings) == 12
    assert all(len(emb) == 768 for emb in embeddings)
