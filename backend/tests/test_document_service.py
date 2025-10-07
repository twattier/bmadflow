"""Unit tests for Document service."""

import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.document import Document
from app.schemas.github import FileInfo
from app.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_store_document_success():
    """Test successful document storage."""
    # Arrange
    mock_repo = AsyncMock()
    project_doc_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    mock_repo.upsert = AsyncMock(return_value=Document(
        id=doc_id,
        project_doc_id=project_doc_id,
        file_path="docs/prd.md",
        file_type="md",
        file_size=13,  # len("# PRD Content") = 13
        content="# PRD Content",
        doc_metadata={"github_commit_sha": "abc123"}
    ))

    service = DocumentService(document_repo=mock_repo)
    file_info = FileInfo(path="docs/prd.md", sha="abc123", type="blob")

    # Act
    result = await service.store_document(
        project_doc_id=project_doc_id,
        file_info=file_info,
        content="# PRD Content",
        commit_sha="abc123"
    )

    # Assert
    assert result.file_path == "docs/prd.md"
    assert result.file_type == "md"
    assert result.file_size == 13
    mock_repo.upsert.assert_called_once_with(
        project_doc_id=project_doc_id,
        file_path="docs/prd.md",
        content="# PRD Content",
        file_type="md",
        file_size=13,
        commit_sha="abc123"
    )


@pytest.mark.asyncio
async def test_store_document_calculates_metadata():
    """Test file_name, file_type, file_size extracted correctly."""
    # Arrange
    mock_repo = AsyncMock()
    project_doc_id = uuid.uuid4()

    captured_args = {}

    async def capture_upsert(**kwargs):
        captured_args.update(kwargs)
        return Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc_id,
            file_path=kwargs["file_path"],
            file_type=kwargs["file_type"],
            file_size=kwargs["file_size"],
            content=kwargs["content"],
            doc_metadata={"github_commit_sha": kwargs["commit_sha"]}
        )

    mock_repo.upsert = capture_upsert

    service = DocumentService(document_repo=mock_repo)

    # Test various file types
    test_cases = [
        ("config/settings.yaml", "yaml"),
        ("data/export.csv", "csv"),
        ("api/schema.json", "json"),
        ("notes.txt", "txt"),
        ("noextension", "txt"),  # Default to txt
    ]

    for file_path, expected_type in test_cases:
        file_info = FileInfo(path=file_path, sha="sha123", type="blob")
        content = "test content"

        # Act
        result = await service.store_document(
            project_doc_id=project_doc_id,
            file_info=file_info,
            content=content,
            commit_sha="sha123"
        )

        # Assert
        assert captured_args["file_type"] == expected_type
        assert captured_args["file_size"] == len(content)
        assert result.file_path == file_path


@pytest.mark.asyncio
async def test_store_document_handles_errors():
    """Test error handling when repository exception occurs."""
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.upsert = AsyncMock(side_effect=Exception("Database error"))

    service = DocumentService(document_repo=mock_repo)
    file_info = FileInfo(path="docs/prd.md", sha="abc123", type="blob")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        await service.store_document(
            project_doc_id=uuid.uuid4(),
            file_info=file_info,
            content="# PRD",
            commit_sha="abc123"
        )

    assert "Database error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_store_documents_batch():
    """Test batch processing of multiple documents."""
    # Arrange
    mock_repo = AsyncMock()
    project_doc_id = uuid.uuid4()

    # Create mock documents for each call
    mock_docs = []
    for i in range(3):
        mock_docs.append(Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc_id,
            file_path=f"file{i}.md",
            file_type="md",
            file_size=10,
            content=f"content{i}",
            doc_metadata={"github_commit_sha": f"sha{i}"}
        ))

    mock_repo.upsert = AsyncMock(side_effect=mock_docs)

    service = DocumentService(document_repo=mock_repo)

    # Prepare batch files
    files = [
        (FileInfo(path="file0.md", sha="sha0", type="blob"), "content0", "sha0"),
        (FileInfo(path="file1.md", sha="sha1", type="blob"), "content1", "sha1"),
        (FileInfo(path="file2.md", sha="sha2", type="blob"), "content2", "sha2"),
    ]

    # Act
    result = await service.store_documents_batch(project_doc_id, files)

    # Assert
    assert len(result) == 3
    assert result[0].file_path == "file0.md"
    assert result[1].file_path == "file1.md"
    assert result[2].file_path == "file2.md"
    assert mock_repo.upsert.call_count == 3


@pytest.mark.asyncio
async def test_store_documents_batch_partial_failure():
    """Test batch processing continues on individual failures."""
    # Arrange
    mock_repo = AsyncMock()
    project_doc_id = uuid.uuid4()

    # Create mock: first succeeds, second fails, third succeeds
    async def upsert_side_effect(**kwargs):
        if kwargs["file_path"] == "file1.md":
            raise Exception("Database error for file1")
        return Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc_id,
            file_path=kwargs["file_path"],
            file_type=kwargs["file_type"],
            file_size=kwargs["file_size"],
            content=kwargs["content"],
            doc_metadata={"github_commit_sha": kwargs["commit_sha"]}
        )

    mock_repo.upsert = AsyncMock(side_effect=upsert_side_effect)

    service = DocumentService(document_repo=mock_repo)

    # Prepare batch files
    files = [
        (FileInfo(path="file0.md", sha="sha0", type="blob"), "content0", "sha0"),
        (FileInfo(path="file1.md", sha="sha1", type="blob"), "content1", "sha1"),  # Will fail
        (FileInfo(path="file2.md", sha="sha2", type="blob"), "content2", "sha2"),
    ]

    # Act
    result = await service.store_documents_batch(project_doc_id, files)

    # Assert
    assert len(result) == 2  # Only successful ones
    assert result[0].file_path == "file0.md"
    assert result[1].file_path == "file2.md"
