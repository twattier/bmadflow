"""Unit tests for ProjectDocService embedding pipeline."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.document import Document
from app.models.project_doc import ProjectDoc
from app.services.project_doc_service import ProjectDocService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_batch_helper_method():
    """Test _batch() helper splits items correctly."""
    # Arrange
    service = ProjectDocService(
        project_doc_repo=MagicMock(),
        github_service=MagicMock(),
        document_service=MagicMock(),
        docling_service=MagicMock(),
        embedding_service=MagicMock(),
        chunk_repository=MagicMock(),
    )

    # Act
    items = list(range(12))  # 12 items
    batches = service._batch(items, 5)

    # Assert
    assert len(batches) == 3  # Should create 3 batches
    assert len(batches[0]) == 5  # First batch: 5 items
    assert len(batches[1]) == 5  # Second batch: 5 items
    assert len(batches[2]) == 2  # Third batch: 2 items
    assert batches[0] == [0, 1, 2, 3, 4]
    assert batches[1] == [5, 6, 7, 8, 9]
    assert batches[2] == [10, 11]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_batch_single_batch():
    """Test _batch() with items less than batch size."""
    # Arrange
    service = ProjectDocService(
        project_doc_repo=MagicMock(),
        github_service=MagicMock(),
        document_service=MagicMock(),
        docling_service=MagicMock(),
        embedding_service=MagicMock(),
        chunk_repository=MagicMock(),
    )

    # Act
    items = list(range(3))  # 3 items, batch size 5
    batches = service._batch(items, 5)

    # Assert
    assert len(batches) == 1  # Single batch
    assert batches[0] == [0, 1, 2]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_batch_empty_list():
    """Test _batch() with empty list."""
    # Arrange
    service = ProjectDocService(
        project_doc_repo=MagicMock(),
        github_service=MagicMock(),
        document_service=MagicMock(),
        docling_service=MagicMock(),
        embedding_service=MagicMock(),
        chunk_repository=MagicMock(),
    )

    # Act
    items = []
    batches = service._batch(items, 5)

    # Assert
    assert len(batches) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_and_embed_document_markdown():
    """Test _process_and_embed_document() with markdown file."""
    # Arrange
    doc_id = uuid.uuid4()
    project_id = uuid.uuid4()

    document = Document(
        id=doc_id,
        project_doc_id=uuid.uuid4(),
        file_path="docs/test.md",
        file_type="md",
        file_size=1024,
        content="# Test\n\n## Section 1\n\nContent here.",
    )

    # Mock chunks from Docling
    mock_chunks = [
        MagicMock(text="Test", index=0, header_anchor="test", metadata={}),
        MagicMock(text="Section 1 Content here.", index=1, header_anchor="section-1", metadata={}),
    ]

    # Mock embeddings from Ollama
    mock_embeddings = [[0.1] * 768, [0.2] * 768]

    # Setup mocks
    mock_docling = AsyncMock()
    mock_docling.process_markdown.return_value = mock_chunks

    mock_embedding_service = AsyncMock()
    mock_embedding_service.generate_embeddings_batch.return_value = mock_embeddings

    mock_chunk_repo = AsyncMock()
    mock_chunk_repo.create_chunks_batch.return_value = []

    service = ProjectDocService(
        project_doc_repo=MagicMock(),
        github_service=MagicMock(),
        document_service=MagicMock(),
        docling_service=mock_docling,
        embedding_service=mock_embedding_service,
        chunk_repository=mock_chunk_repo,
    )

    # Act
    embeddings_count = await service._process_and_embed_document(document, project_id)

    # Assert
    assert embeddings_count == 2
    mock_docling.process_markdown.assert_called_once_with(document.content)
    mock_embedding_service.generate_embeddings_batch.assert_called_once()
    mock_chunk_repo.create_chunks_batch.assert_called_once()

    # Verify chunk create objects structure
    call_args = mock_chunk_repo.create_chunks_batch.call_args[0][0]
    assert len(call_args) == 2
    assert call_args[0].document_id == doc_id
    assert call_args[0].chunk_text == "Test"
    assert call_args[0].embedding == [0.1] * 768
    assert call_args[0].header_anchor == "test"
    assert call_args[0].metadata["file_path"] == "docs/test.md"
    assert call_args[0].metadata["file_name"] == "test.md"
    assert call_args[0].metadata["file_type"] == "md"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_and_embed_document_csv():
    """Test _process_and_embed_document() with CSV file."""
    # Arrange
    doc_id = uuid.uuid4()
    project_id = uuid.uuid4()

    document = Document(
        id=doc_id,
        project_doc_id=uuid.uuid4(),
        file_path="data/test.csv",
        file_type="csv",
        file_size=512,
        content="name,value\nrow1,100\nrow2,200",
    )

    mock_chunks = [
        MagicMock(text="name,value\nrow1,100", index=0, header_anchor=None, metadata={}),
    ]

    mock_embeddings = [[0.1] * 768]

    # Setup mocks
    mock_docling = AsyncMock()
    mock_docling.process_csv.return_value = mock_chunks

    mock_embedding_service = AsyncMock()
    mock_embedding_service.generate_embeddings_batch.return_value = mock_embeddings

    mock_chunk_repo = AsyncMock()
    mock_chunk_repo.create_chunks_batch.return_value = []

    service = ProjectDocService(
        project_doc_repo=MagicMock(),
        github_service=MagicMock(),
        document_service=MagicMock(),
        docling_service=mock_docling,
        embedding_service=mock_embedding_service,
        chunk_repository=mock_chunk_repo,
    )

    # Act
    embeddings_count = await service._process_and_embed_document(document, project_id)

    # Assert
    assert embeddings_count == 1
    mock_docling.process_csv.assert_called_once_with(document.content)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_and_embed_document_unsupported_type():
    """Test _process_and_embed_document() with unsupported file type."""
    # Arrange
    document = Document(
        id=uuid.uuid4(),
        project_doc_id=uuid.uuid4(),
        file_path="image.png",
        file_type="png",
        file_size=1024,
        content="binary data",
    )

    service = ProjectDocService(
        project_doc_repo=MagicMock(),
        github_service=MagicMock(),
        document_service=MagicMock(),
        docling_service=AsyncMock(),
        embedding_service=AsyncMock(),
        chunk_repository=AsyncMock(),
    )

    # Act
    embeddings_count = await service._process_and_embed_document(document, uuid.uuid4())

    # Assert
    assert embeddings_count == 0  # No embeddings for unsupported type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_and_embed_document_empty_chunks():
    """Test _process_and_embed_document() when no chunks generated."""
    # Arrange
    document = Document(
        id=uuid.uuid4(),
        project_doc_id=uuid.uuid4(),
        file_path="docs/empty.md",
        file_type="md",
        file_size=0,
        content="",
    )

    mock_docling = AsyncMock()
    mock_docling.process_markdown.return_value = []  # No chunks

    service = ProjectDocService(
        project_doc_repo=MagicMock(),
        github_service=MagicMock(),
        document_service=MagicMock(),
        docling_service=mock_docling,
        embedding_service=AsyncMock(),
        chunk_repository=AsyncMock(),
    )

    # Act
    embeddings_count = await service._process_and_embed_document(document, uuid.uuid4())

    # Assert
    assert embeddings_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sync_with_embedding_pipeline_success():
    """Test full sync with embedding pipeline - success case."""
    # Arrange
    project_doc_id = uuid.uuid4()
    project_id = uuid.uuid4()

    project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=project_id,
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    # Mock stored documents
    mock_docs = [
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc_id,
            file_path="docs/file1.md",
            file_type="md",
            file_size=1024,
            content="# File 1",
        ),
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc_id,
            file_path="docs/file2.md",
            file_type="md",
            file_size=1024,
            content="# File 2",
        ),
    ]

    # Mock chunks
    mock_chunks = [
        MagicMock(text="Chunk 1", index=0, header_anchor="section-1", metadata={}),
    ]

    mock_embeddings = [[0.1] * 768]

    # Setup mocks
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = project_doc

    mock_github = AsyncMock()
    mock_github.fetch_repository_tree.return_value = []
    mock_github.get_last_commit_date.return_value = MagicMock()

    mock_doc_service = AsyncMock()
    mock_doc_service.store_documents_batch.return_value = mock_docs

    mock_docling = AsyncMock()
    mock_docling.process_markdown.return_value = mock_chunks

    mock_embedding_service = AsyncMock()
    mock_embedding_service.generate_embeddings_batch.return_value = mock_embeddings

    mock_chunk_repo = AsyncMock()
    mock_chunk_repo.create_chunks_batch.return_value = []

    mock_db = AsyncMock()

    service = ProjectDocService(
        project_doc_repo=mock_repo,
        github_service=mock_github,
        document_service=mock_doc_service,
        docling_service=mock_docling,
        embedding_service=mock_embedding_service,
        chunk_repository=mock_chunk_repo,
    )

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is True
    assert result.files_synced == 2
    assert result.embeddings_created == 2  # 1 embedding per document
    assert result.files_failed == 0
    assert len(result.errors) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sync_with_embedding_failure_continues():
    """Test sync continues when embedding fails for one document."""
    # Arrange
    project_doc_id = uuid.uuid4()
    project_id = uuid.uuid4()

    project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=project_id,
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    # Mock stored documents
    mock_docs = [
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc_id,
            file_path="docs/success.md",
            file_type="md",
            file_size=1024,
            content="# Success",
        ),
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc_id,
            file_path="docs/failure.md",
            file_type="md",
            file_size=1024,
            content="# Failure",
        ),
    ]

    # Mock chunks
    mock_chunks = [
        MagicMock(text="Chunk", index=0, header_anchor=None, metadata={}),
    ]

    mock_embeddings = [[0.1] * 768]

    # Setup mocks
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = project_doc

    mock_github = AsyncMock()
    mock_github.fetch_repository_tree.return_value = []
    mock_github.get_last_commit_date.return_value = MagicMock()

    mock_doc_service = AsyncMock()
    mock_doc_service.store_documents_batch.return_value = mock_docs

    mock_docling = AsyncMock()
    mock_docling.process_markdown.return_value = mock_chunks

    # Mock embedding service to fail on second call
    call_count = [0]

    async def mock_generate_embeddings(texts):
        call_count[0] += 1
        if call_count[0] == 2:
            raise ConnectionError("Ollama unavailable")
        return mock_embeddings

    mock_embedding_service = AsyncMock()
    mock_embedding_service.generate_embeddings_batch.side_effect = mock_generate_embeddings

    mock_chunk_repo = AsyncMock()
    mock_chunk_repo.create_chunks_batch.return_value = []

    mock_db = AsyncMock()

    service = ProjectDocService(
        project_doc_repo=mock_repo,
        github_service=mock_github,
        document_service=mock_doc_service,
        docling_service=mock_docling,
        embedding_service=mock_embedding_service,
        chunk_repository=mock_chunk_repo,
    )

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is True  # Overall success
    assert result.files_synced == 2  # Both files stored
    assert result.embeddings_created == 1  # Only 1 embedded successfully
    assert result.files_failed == 1  # 1 failed embedding
    assert len(result.errors) == 1
    assert "failure.md" in result.errors[0]
