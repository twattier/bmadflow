"""Unit tests for VectorStorageService."""

import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.chunk import Chunk
from app.services.vector_storage_service import VectorStorageService


@pytest.mark.asyncio
async def test_store_chunk_success():
    """Test storing a single chunk with metadata."""
    # Arrange
    mock_chunk_repo = AsyncMock()
    service = VectorStorageService(mock_chunk_repo)

    document_id = uuid.uuid4()
    chunk_text = "Test chunk content"
    chunk_index = 0
    embedding = [0.1] * 768
    header_anchor = "test-section"
    file_path = "docs/test.md"
    file_name = "test.md"
    file_type = "md"
    total_chunks = 5

    # Mock repository response
    mock_chunk = Chunk(
        id=uuid.uuid4(),
        document_id=document_id,
        chunk_text=chunk_text,
        chunk_index=chunk_index,
        embedding=embedding,
        header_anchor=header_anchor,
        chunk_metadata={
            "file_path": file_path,
            "file_name": file_name,
            "file_type": file_type,
            "chunk_position": chunk_index,
            "total_chunks": total_chunks,
        },
    )
    mock_chunk_repo.create_chunk.return_value = mock_chunk

    # Act
    chunk = await service.store_chunk(
        document_id=document_id,
        chunk_text=chunk_text,
        chunk_index=chunk_index,
        embedding=embedding,
        header_anchor=header_anchor,
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        total_chunks=total_chunks,
    )

    # Assert
    assert chunk.chunk_text == chunk_text
    assert chunk.chunk_index == chunk_index
    assert chunk.chunk_metadata["file_path"] == file_path
    assert chunk.chunk_metadata["file_name"] == file_name
    assert chunk.chunk_metadata["file_type"] == file_type
    assert chunk.chunk_metadata["chunk_position"] == chunk_index
    assert chunk.chunk_metadata["total_chunks"] == total_chunks
    mock_chunk_repo.create_chunk.assert_called_once()


@pytest.mark.asyncio
async def test_store_chunk_invalid_embedding_dim():
    """Test storing chunk with invalid embedding dimension."""
    # Arrange
    mock_chunk_repo = AsyncMock()
    service = VectorStorageService(mock_chunk_repo)

    document_id = uuid.uuid4()
    invalid_embedding = [0.1] * 512  # Wrong dimension

    # Act & Assert
    with pytest.raises(ValueError, match="Embedding must be 768 dimensions"):
        await service.store_chunk(
            document_id=document_id,
            chunk_text="Test chunk",
            chunk_index=0,
            embedding=invalid_embedding,
            header_anchor=None,
            file_path="test.md",
            file_name="test.md",
            file_type="md",
            total_chunks=1,
        )


@pytest.mark.asyncio
async def test_store_chunks_batch():
    """Test bulk storing multiple chunks."""
    # Arrange
    mock_chunk_repo = AsyncMock()
    service = VectorStorageService(mock_chunk_repo)

    document_id = uuid.uuid4()
    chunks_data = [
        {
            "document_id": document_id,
            "chunk_text": f"Chunk {i} content",
            "chunk_index": i,
            "embedding": [0.1] * 768,
            "header_anchor": f"section-{i}",
            "metadata": {
                "file_path": "test.md",
                "file_name": "test.md",
                "file_type": "md",
                "chunk_position": i,
                "total_chunks": 3,
            },
        }
        for i in range(3)
    ]

    # Mock repository response
    mock_chunks = [Chunk(id=uuid.uuid4(), **data) for data in chunks_data]
    mock_chunk_repo.create_chunks_batch.return_value = mock_chunks

    # Act
    chunks = await service.store_chunks_batch(chunks_data)

    # Assert
    assert len(chunks) == 3
    mock_chunk_repo.create_chunks_batch.assert_called_once()


@pytest.mark.asyncio
async def test_metadata_construction():
    """Test metadata JSONB structure construction."""
    # Arrange
    mock_chunk_repo = AsyncMock()
    service = VectorStorageService(mock_chunk_repo)

    document_id = uuid.uuid4()
    chunk_text = "Test chunk"
    chunk_index = 2
    embedding = [0.1] * 768
    header_anchor = "introduction"
    file_path = "docs/architecture/database-schema.md"
    file_name = "database-schema.md"
    file_type = "md"
    total_chunks = 10

    # Mock repository
    mock_chunk_repo.create_chunk.return_value = Chunk(
        id=uuid.uuid4(),
        document_id=document_id,
        chunk_text=chunk_text,
        chunk_index=chunk_index,
        embedding=embedding,
        header_anchor=header_anchor,
        chunk_metadata={
            "file_path": file_path,
            "file_name": file_name,
            "file_type": file_type,
            "chunk_position": chunk_index,
            "total_chunks": total_chunks,
        },
    )

    # Act
    chunk = await service.store_chunk(
        document_id=document_id,
        chunk_text=chunk_text,
        chunk_index=chunk_index,
        embedding=embedding,
        header_anchor=header_anchor,
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        total_chunks=total_chunks,
    )

    # Assert: Verify metadata structure matches AC4
    metadata = chunk.chunk_metadata
    assert "file_path" in metadata
    assert "file_name" in metadata
    assert "file_type" in metadata
    assert "chunk_position" in metadata
    assert "total_chunks" in metadata
    assert metadata["file_path"] == file_path
    assert metadata["file_name"] == file_name
    assert metadata["file_type"] == file_type
    assert metadata["chunk_position"] == chunk_index
    assert metadata["total_chunks"] == total_chunks


@pytest.mark.asyncio
async def test_header_anchor_null():
    """Test graceful handling when header_anchor is None."""
    # Arrange
    mock_chunk_repo = AsyncMock()
    service = VectorStorageService(mock_chunk_repo)

    document_id = uuid.uuid4()
    embedding = [0.1] * 768

    # Mock repository
    mock_chunk_repo.create_chunk.return_value = Chunk(
        id=uuid.uuid4(),
        document_id=document_id,
        chunk_text="Test chunk",
        chunk_index=0,
        embedding=embedding,
        header_anchor=None,  # Nullable per AC5
        chunk_metadata={
            "file_path": "test.md",
            "file_name": "test.md",
            "file_type": "md",
            "chunk_position": 0,
            "total_chunks": 1,
        },
    )

    # Act
    chunk = await service.store_chunk(
        document_id=document_id,
        chunk_text="Test chunk",
        chunk_index=0,
        embedding=embedding,
        header_anchor=None,  # None is valid
        file_path="test.md",
        file_name="test.md",
        file_type="md",
        total_chunks=1,
    )

    # Assert
    assert chunk.header_anchor is None
    mock_chunk_repo.create_chunk.assert_called_once()
