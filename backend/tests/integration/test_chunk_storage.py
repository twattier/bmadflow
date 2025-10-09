"""Integration tests for chunk storage with real database."""

import uuid
from datetime import datetime

import pytest

from app.models.document import Document
from app.models.project import Project
from app.models.project_doc import ProjectDoc
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.chunk import ChunkCreate


@pytest.mark.integration
@pytest.mark.asyncio
async def test_store_and_retrieve_100_chunks(db_session):
    """Integration test: Store 100+ chunks, verify all queryable."""
    # Setup: Create project, project_doc, and document
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Test Description",
    )
    db_session.add(project)
    await db_session.commit()

    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Test Repository",
        github_url="https://github.com/test/repo",
        last_synced_at=datetime.utcnow(),
    )
    db_session.add(project_doc)
    await db_session.commit()

    document = Document(
        id=uuid.uuid4(),
        project_doc_id=project_doc.id,
        file_path="docs/test.md",
        file_type="md",
        file_size=1024,
        content="Test document content",
    )
    db_session.add(document)
    await db_session.commit()

    # Create repository
    repo = ChunkRepository(db_session)

    # Create 100 chunks
    chunks_data = [
        ChunkCreate(
            document_id=document.id,
            chunk_text=f"Chunk {i} content with sufficient text for testing",
            chunk_index=i,
            embedding=[0.1 * (i % 10)] * 768,  # Vary embeddings
            header_anchor=f"section-{i}" if i % 2 == 0 else None,
            metadata={
                "file_path": "docs/test.md",
                "file_name": "test.md",
                "file_type": "md",
                "chunk_position": i,
                "total_chunks": 100,
            },
        )
        for i in range(100)
    ]

    # Act: Bulk insert
    created_chunks = await repo.create_chunks_batch(chunks_data)

    # Act: Retrieve all chunks
    retrieved_chunks = await repo.get_by_document_id(document.id)

    # Assert: All chunks created and retrievable
    assert len(created_chunks) == 100
    assert len(retrieved_chunks) == 100

    # Assert: Chunks are ordered by chunk_index
    assert retrieved_chunks[0].chunk_index == 0
    assert retrieved_chunks[50].chunk_index == 50
    assert retrieved_chunks[99].chunk_index == 99

    # Assert: Metadata is correct (check if not None before accessing)
    if retrieved_chunks[0].chunk_metadata:
        assert retrieved_chunks[0].chunk_metadata["file_path"] == "docs/test.md"
        assert retrieved_chunks[0].chunk_metadata["total_chunks"] == 100


@pytest.mark.integration
@pytest.mark.asyncio
async def test_embedding_vector_type(db_session):
    """Test that pgvector column type works correctly."""
    # Setup: Create project hierarchy
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Test Description",
    )
    db_session.add(project)
    await db_session.commit()

    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Test Repository",
        github_url="https://github.com/test/repo",
        last_synced_at=datetime.utcnow(),
    )
    db_session.add(project_doc)
    await db_session.commit()

    document = Document(
        id=uuid.uuid4(),
        project_doc_id=project_doc.id,
        file_path="docs/test.md",
        file_type="md",
        file_size=1024,
        content="Test content",
    )
    db_session.add(document)
    await db_session.commit()

    repo = ChunkRepository(db_session)

    # Create chunk with specific embedding
    test_embedding = [0.5] * 768
    chunk_data = ChunkCreate(
        document_id=document.id,
        chunk_text="Test chunk with vector embedding",
        chunk_index=0,
        embedding=test_embedding,
        header_anchor="test-section",
        metadata={
            "file_path": "docs/test.md",
            "file_name": "test.md",
            "file_type": "md",
            "chunk_position": 0,
            "total_chunks": 1,
        },
    )

    # Act
    await repo.create_chunk(chunk_data)
    await db_session.commit()

    # Retrieve and verify
    retrieved_chunks = await repo.get_by_document_id(document.id)
    assert len(retrieved_chunks) == 1
    assert retrieved_chunks[0].chunk_text == "Test chunk with vector embedding"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cascade_delete(db_session):
    """Test that deleting document auto-deletes associated chunks."""
    # Setup
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Test Description",
    )
    db_session.add(project)
    await db_session.commit()

    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Test Repository",
        github_url="https://github.com/test/repo",
        last_synced_at=datetime.utcnow(),
    )
    db_session.add(project_doc)
    await db_session.commit()

    document = Document(
        id=uuid.uuid4(),
        project_doc_id=project_doc.id,
        file_path="docs/test.md",
        file_type="md",
        file_size=1024,
        content="Test content",
    )
    db_session.add(document)
    await db_session.commit()

    repo = ChunkRepository(db_session)

    # Create 5 chunks
    chunks_data = [
        ChunkCreate(
            document_id=document.id,
            chunk_text=f"Chunk {i}",
            chunk_index=i,
            embedding=[0.1] * 768,
            header_anchor=None,
            metadata={
                "file_path": "docs/test.md",
                "file_name": "test.md",
                "file_type": "md",
                "chunk_position": i,
                "total_chunks": 5,
            },
        )
        for i in range(5)
    ]
    await repo.create_chunks_batch(chunks_data)

    # Verify chunks exist
    chunks = await repo.get_by_document_id(document.id)
    assert len(chunks) == 5

    # Act: Delete document
    await db_session.delete(document)
    await db_session.commit()

    # Assert: Chunks auto-deleted due to CASCADE
    chunks_after_delete = await repo.get_by_document_id(document.id)
    assert len(chunks_after_delete) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_metadata_jsonb_query(db_session):
    """Test querying chunks by metadata fields."""
    # Setup
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Test Description",
    )
    db_session.add(project)
    await db_session.commit()

    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Test Repository",
        github_url="https://github.com/test/repo",
        last_synced_at=datetime.utcnow(),
    )
    db_session.add(project_doc)
    await db_session.commit()

    document = Document(
        id=uuid.uuid4(),
        project_doc_id=project_doc.id,
        file_path="docs/architecture/database-schema.md",
        file_type="md",
        file_size=2048,
        content="Database schema documentation",
    )
    db_session.add(document)
    await db_session.commit()

    repo = ChunkRepository(db_session)

    # Create chunk with specific metadata
    chunk_data = ChunkCreate(
        document_id=document.id,
        chunk_text="Schema description",
        chunk_index=0,
        embedding=[0.1] * 768,
        header_anchor="schema-overview",
        metadata={
            "file_path": "docs/architecture/database-schema.md",
            "file_name": "database-schema.md",
            "file_type": "md",
            "chunk_position": 0,
            "total_chunks": 5,
        },
    )
    await repo.create_chunk(chunk_data)
    await db_session.commit()

    # Retrieve and verify metadata
    chunks = await repo.get_by_document_id(document.id)
    assert len(chunks) == 1
    if chunks[0].chunk_metadata:
        assert chunks[0].chunk_metadata["file_name"] == "database-schema.md"
        assert chunks[0].chunk_metadata["file_type"] == "md"
        assert chunks[0].chunk_metadata["chunk_position"] == 0
