"""Unit tests for ChunkRepository."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.chunk import ChunkCreate


@pytest.mark.asyncio
async def test_create_chunk_success():
    """Test creating a single chunk successfully."""
    # Arrange
    mock_db = AsyncMock()
    repo = ChunkRepository(mock_db)

    chunk_data = ChunkCreate(
        document_id=uuid.uuid4(),
        chunk_text="Test chunk content",
        chunk_index=0,
        embedding=[0.1] * 768,
        header_anchor="test-section",
        metadata={
            "file_path": "test.md",
            "file_name": "test.md",
            "file_type": "md",
            "chunk_position": 0,
            "total_chunks": 1,
        },
    )

    # Mock the Chunk creation and refresh
    mock_chunk = Chunk(**chunk_data.model_dump())
    mock_chunk.id = uuid.uuid4()

    # Mock refresh to return the chunk with ID
    async def mock_refresh(obj):
        obj.id = mock_chunk.id

    mock_db.refresh = mock_refresh

    # Act
    chunk = await repo.create_chunk(chunk_data)

    # Assert
    assert chunk.chunk_text == "Test chunk content"
    assert chunk.chunk_index == 0
    assert chunk.header_anchor == "test-section"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_chunks_batch():
    """Test bulk inserting multiple chunks."""
    # Arrange
    mock_db = AsyncMock()
    repo = ChunkRepository(mock_db)

    document_id = uuid.uuid4()
    chunks_data = [
        ChunkCreate(
            document_id=document_id,
            chunk_text=f"Chunk {i} content",
            chunk_index=i,
            embedding=[0.1] * 768,
            header_anchor=f"section-{i}",
            metadata={
                "file_path": "test.md",
                "file_name": "test.md",
                "file_type": "md",
                "chunk_position": i,
                "total_chunks": 3,
            },
        )
        for i in range(3)
    ]

    # Act
    chunks = await repo.create_chunks_batch(chunks_data)

    # Assert
    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2
    mock_db.add_all.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_document_id():
    """Test retrieving chunks by document ID in order."""
    # Arrange
    mock_db = AsyncMock()
    repo = ChunkRepository(mock_db)

    document_id = uuid.uuid4()

    # Mock query result
    mock_chunks = [
        MagicMock(chunk_index=0, chunk_text="First chunk"),
        MagicMock(chunk_index=1, chunk_text="Second chunk"),
        MagicMock(chunk_index=2, chunk_text="Third chunk"),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_chunks
    mock_db.execute.return_value = mock_result

    # Act
    chunks = await repo.get_by_document_id(document_id)

    # Assert
    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_count_by_project_id():
    """Test counting chunks for a project."""
    # Arrange
    mock_db = AsyncMock()
    repo = ChunkRepository(mock_db)

    project_id = uuid.uuid4()

    # Mock count result
    mock_result = MagicMock()
    mock_result.scalar.return_value = 42
    mock_db.execute.return_value = mock_result

    # Act
    count = await repo.count_by_project_id(project_id)

    # Assert
    assert count == 42
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_foreign_key_violation():
    """Test handling foreign key violation when document_id doesn't exist."""
    # Arrange
    mock_db = AsyncMock()
    repo = ChunkRepository(mock_db)

    chunk_data = ChunkCreate(
        document_id=uuid.uuid4(),  # Non-existent document
        chunk_text="Test chunk",
        chunk_index=0,
        embedding=[0.1] * 768,
        header_anchor=None,
        metadata={
            "file_path": "test.md",
            "file_name": "test.md",
            "file_type": "md",
            "chunk_position": 0,
            "total_chunks": 1,
        },
    )

    # Mock commit to raise IntegrityError
    from sqlalchemy.exc import IntegrityError

    mock_db.commit.side_effect = IntegrityError("FK violation", None, None)

    # Act & Assert
    with pytest.raises(IntegrityError):
        await repo.create_chunk(chunk_data)
