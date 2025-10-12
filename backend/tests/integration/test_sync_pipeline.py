"""Integration tests for sync-to-embedding pipeline."""

import uuid
from datetime import datetime
from typing import List
from unittest.mock import AsyncMock, patch

import pytest

from app.models.project import Project
from app.models.project_doc import ProjectDoc
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_doc import ProjectDocRepository
from app.schemas.github import FileInfo
from app.services.docling_service import DoclingService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService
from app.services.project_doc_service import ProjectDocService


@pytest.fixture
async def test_project(db_session):
    """Create a test project."""
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Test project for sync pipeline",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
async def test_project_doc(db_session, test_project):
    """Create a test project_doc."""
    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=test_project.id,
        name="Test Repository",
        github_url="https://github.com/test/repo",
        github_folder_path="docs",
    )
    db_session.add(project_doc)
    await db_session.commit()
    await db_session.refresh(project_doc)
    return project_doc


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sync_pipeline_end_to_end(db_session, test_project_doc, test_project):
    """
    Integration test: Full sync → verify documents + chunks tables populated.

    Tests the complete pipeline:
    1. Fetch GitHub file tree (mocked)
    2. Download file contents (mocked)
    3. Store documents
    4. Chunk documents with Docling
    5. Generate embeddings with Ollama (mocked)
    6. Store chunks with embeddings
    """
    # Mock GitHub file tree response
    mock_files = [
        FileInfo(path="docs/README.md", sha="abc123", type="blob", size=1024),
        FileInfo(path="docs/guide.md", sha="def456", type="blob", size=2048),
        FileInfo(path="docs/api.md", sha="ghi789", type="blob", size=1536),
    ]

    # Mock file contents
    mock_contents = {
        "docs/README.md": "# README\n\nThis is a test document.\n\n## Section 1\n\nContent here.",
        "docs/guide.md": "# Guide\n\n## Getting Started\n\nStep 1: Install.\n\n## Usage\n\nUse it.",
        "docs/api.md": "# API Reference\n\n## Endpoints\n\n### GET /api\n\nReturns data.",
    }

    # Mock Ollama embedding response (768-dim vector)
    mock_embedding = [0.1] * 768

    # Setup mocked services
    with (
        patch.object(GitHubService, "fetch_repository_tree", new_callable=AsyncMock) as mock_tree,
        patch.object(
            GitHubService, "download_file_content", new_callable=AsyncMock
        ) as mock_download,
        patch.object(
            GitHubService, "get_last_commit_date", new_callable=AsyncMock
        ) as mock_commit_date,
        patch.object(
            EmbeddingService, "generate_embeddings_batch", new_callable=AsyncMock
        ) as mock_embeddings,
    ):

        # Configure mocks
        mock_tree.return_value = mock_files
        mock_download.side_effect = lambda url, path: (
            mock_contents[path],
            "abc123",
        )
        mock_commit_date.return_value = datetime.utcnow()
        mock_embeddings.return_value = [mock_embedding] * 10  # Return embeddings for all chunks

        # Initialize services
        project_doc_repo = ProjectDocRepository()
        document_repo = DocumentRepository(db_session)
        document_service = DocumentService(document_repo)
        github_service = GitHubService()
        docling_service = DoclingService()
        embedding_service = EmbeddingService()
        chunk_repository = ChunkRepository(db_session)

        project_doc_service = ProjectDocService(
            project_doc_repo=project_doc_repo,
            github_service=github_service,
            document_service=document_service,
            docling_service=docling_service,
            embedding_service=embedding_service,
            chunk_repository=chunk_repository,
        )

        # Act: Trigger sync
        result = await project_doc_service.sync_project_doc(db_session, test_project_doc.id)

        # Assert: Sync completed successfully
        assert result.success is True
        assert result.files_synced == 3
        assert result.embeddings_created > 0
        assert result.files_failed == 0
        assert len(result.errors) == 0
        assert result.duration_seconds > 0

        # Verify: Documents table populated
        documents = await document_repo.get_by_project_doc_id(test_project_doc.id)
        assert len(documents) == 3

        # Verify: Chunks table populated with embeddings
        total_chunks = 0
        for doc in documents:
            chunks = await chunk_repository.get_by_document_id(doc.id)
            assert len(chunks) > 0  # Each document should have chunks
            total_chunks += len(chunks)

            # Verify chunk structure
            for chunk in chunks:
                assert chunk.chunk_text is not None
                assert len(chunk.embedding) == 768  # Verify embedding dimension
                assert chunk.chunk_metadata is not None
                assert "file_path" in chunk.chunk_metadata
                assert "file_name" in chunk.chunk_metadata
                assert "file_type" in chunk.chunk_metadata

        # Verify total embeddings created matches result
        assert result.embeddings_created == total_chunks


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sync_with_partial_failure(db_session, test_project_doc, test_project):
    """
    Integration test: Mock Ollama to fail on 1 file, others succeed.

    Verifies that:
    - Sync continues when one file fails
    - failed_files list contains failed file path
    - Other files are successfully indexed
    """
    # Mock GitHub responses
    mock_files = [
        FileInfo(path="docs/success1.md", sha="sha001", type="blob", size=1024),
        FileInfo(path="docs/failure.md", sha="sha002", type="blob", size=1024),
        FileInfo(path="docs/success2.md", sha="sha003", type="blob", size=1024),
    ]

    mock_contents = {
        "docs/success1.md": "# Success 1\n\nThis will succeed.",
        "docs/failure.md": "# Failure\n\nThis will fail.",
        "docs/success2.md": "# Success 2\n\nThis will also succeed.",
    }

    # Mock embedding service to fail on second file
    mock_embedding = [0.1] * 768
    call_count = [0]

    async def mock_generate_embeddings(texts: List[str]) -> List[List[float]]:
        """Mock that fails on second document."""
        call_count[0] += 1
        # Fail on second document
        if call_count[0] == 2:
            raise ConnectionError("Ollama service unavailable")
        return [mock_embedding] * len(texts)

    with (
        patch.object(GitHubService, "fetch_repository_tree", new_callable=AsyncMock) as mock_tree,
        patch.object(
            GitHubService, "download_file_content", new_callable=AsyncMock
        ) as mock_download,
        patch.object(
            GitHubService, "get_last_commit_date", new_callable=AsyncMock
        ) as mock_commit_date,
        patch.object(
            EmbeddingService, "generate_embeddings_batch", new_callable=AsyncMock
        ) as mock_embeddings,
    ):

        # Configure mocks
        mock_tree.return_value = mock_files
        mock_download.side_effect = lambda url, path: (mock_contents[path], "abc123")
        mock_commit_date.return_value = datetime.utcnow()
        mock_embeddings.side_effect = mock_generate_embeddings

        # Initialize services
        project_doc_repo = ProjectDocRepository()
        document_repo = DocumentRepository(db_session)
        document_service = DocumentService(document_repo)
        github_service = GitHubService()
        docling_service = DoclingService()
        embedding_service = EmbeddingService()
        chunk_repository = ChunkRepository(db_session)

        project_doc_service = ProjectDocService(
            project_doc_repo=project_doc_repo,
            github_service=github_service,
            document_service=document_service,
            docling_service=docling_service,
            embedding_service=embedding_service,
            chunk_repository=chunk_repository,
        )

        # Act: Trigger sync
        result = await project_doc_service.sync_project_doc(db_session, test_project_doc.id)

        # Assert: Sync completed with partial failure
        assert result.success is True
        assert result.files_synced == 3  # All files downloaded and stored
        assert result.files_failed == 1  # One file failed embedding
        assert len(result.errors) == 1
        assert "failure.md" in result.errors[0]

        # Verify: 2 documents successfully embedded
        documents = await document_repo.get_by_project_doc_id(test_project_doc.id)
        assert len(documents) == 3

        # Verify: Only successful documents have chunks
        chunks_count = 0
        for doc in documents:
            chunks = await chunk_repository.get_by_document_id(doc.id)
            if "failure.md" not in doc.file_path:
                assert len(chunks) > 0  # Successful files have chunks
                chunks_count += len(chunks)
            else:
                assert len(chunks) == 0  # Failed file has no chunks

        assert result.embeddings_created == chunks_count


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skip(reason="Performance test - run manually with real Ollama")
async def test_sync_performance_5min_limit(db_session, test_project_doc, test_project):
    """
    Performance test: 20 files complete in <5 min.

    This test is skipped by default as it requires:
    - Real Ollama service running
    - 20 markdown files
    - Significant execution time

    To run: pytest -v -m integration -k test_sync_performance
    """
    # Create 20 test markdown files
    mock_files = [
        FileInfo(path=f"docs/file{i:02d}.md", sha=f"sha{i:03d}", type="blob", size=1024)
        for i in range(20)
    ]

    # Generate varied content for each file
    mock_contents = {
        f"docs/file{i:02d}.md": f"""# File {i}

## Introduction
This is test file number {i} for performance testing.

## Section 1
Content for section 1 in file {i}.

## Section 2
More content for section 2 in file {i}.

## Conclusion
Final section for file {i}.
"""
        for i in range(20)
    }

    with (
        patch.object(GitHubService, "fetch_repository_tree", new_callable=AsyncMock) as mock_tree,
        patch.object(
            GitHubService, "download_file_content", new_callable=AsyncMock
        ) as mock_download,
        patch.object(
            GitHubService, "get_last_commit_date", new_callable=AsyncMock
        ) as mock_commit_date,
    ):

        mock_tree.return_value = mock_files
        mock_download.side_effect = lambda url, path: (mock_contents[path], "abc123")
        mock_commit_date.return_value = datetime.utcnow()

        # Initialize services (with REAL Ollama)
        project_doc_repo = ProjectDocRepository()
        document_repo = DocumentRepository(db_session)
        document_service = DocumentService(document_repo)
        github_service = GitHubService()
        docling_service = DoclingService()
        embedding_service = EmbeddingService()  # Real service
        chunk_repository = ChunkRepository(db_session)

        project_doc_service = ProjectDocService(
            project_doc_repo=project_doc_repo,
            github_service=github_service,
            document_service=document_service,
            docling_service=docling_service,
            embedding_service=embedding_service,
            chunk_repository=chunk_repository,
        )

        # Act: Trigger sync and measure duration
        result = await project_doc_service.sync_project_doc(db_session, test_project_doc.id)

        # Assert: Completed within 5 minutes
        assert (
            result.duration_seconds < 300
        ), f"Sync took {result.duration_seconds:.2f}s, exceeds 5min threshold"
        assert result.success is True
        assert result.files_synced == 20


@pytest.mark.integration
@pytest.mark.asyncio
async def test_embedding_metadata_complete(db_session, test_project_doc, test_project):
    """
    Integration test: Verify all metadata fields populated in embeddings.

    Checks that each chunk has:
    - file_path
    - file_name
    - file_type
    - chunk_position
    - total_chunks
    """
    # Mock single file
    mock_files = [FileInfo(path="docs/test.md", sha="test123", type="blob", size=1024)]
    mock_content = "# Test\n\n## Section 1\n\nContent here.\n\n## Section 2\n\nMore content."

    mock_embedding = [0.1] * 768

    with (
        patch.object(GitHubService, "fetch_repository_tree", new_callable=AsyncMock) as mock_tree,
        patch.object(
            GitHubService, "download_file_content", new_callable=AsyncMock
        ) as mock_download,
        patch.object(
            GitHubService, "get_last_commit_date", new_callable=AsyncMock
        ) as mock_commit_date,
        patch.object(
            EmbeddingService, "generate_embeddings_batch", new_callable=AsyncMock
        ) as mock_embeddings,
    ):

        mock_tree.return_value = mock_files
        mock_download.return_value = (mock_content, "abc123")
        mock_commit_date.return_value = datetime.utcnow()
        mock_embeddings.return_value = [mock_embedding] * 10

        # Initialize services
        project_doc_repo = ProjectDocRepository()
        document_repo = DocumentRepository(db_session)
        document_service = DocumentService(document_repo)
        github_service = GitHubService()
        docling_service = DoclingService()
        embedding_service = EmbeddingService()
        chunk_repository = ChunkRepository(db_session)

        project_doc_service = ProjectDocService(
            project_doc_repo=project_doc_repo,
            github_service=github_service,
            document_service=document_service,
            docling_service=docling_service,
            embedding_service=embedding_service,
            chunk_repository=chunk_repository,
        )

        # Act
        await project_doc_service.sync_project_doc(db_session, test_project_doc.id)

        # Get document and chunks
        documents = await document_repo.get_by_project_doc_id(test_project_doc.id)
        assert len(documents) == 1

        chunks = await chunk_repository.get_by_document_id(documents[0].id)
        assert len(chunks) > 0

        # Verify metadata fields
        for chunk in chunks:
            assert chunk.chunk_metadata is not None
            assert "file_path" in chunk.chunk_metadata
            assert "file_name" in chunk.chunk_metadata
            assert "file_type" in chunk.chunk_metadata
            assert "chunk_position" in chunk.chunk_metadata
            assert "total_chunks" in chunk.chunk_metadata

            # Verify values
            assert chunk.chunk_metadata["file_path"] == "docs/test.md"
            assert chunk.chunk_metadata["file_name"] == "test.md"
            assert chunk.chunk_metadata["file_type"] == "md"
            assert isinstance(chunk.chunk_metadata["chunk_position"], int)
            assert chunk.chunk_metadata["total_chunks"] == len(chunks)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_header_anchors_extracted(db_session, test_project_doc, test_project):
    """
    Integration test: Verify 90%+ chunks have header anchors.

    Tests that header anchor extraction from Story 4.4 is working
    in the sync pipeline.
    """
    # Mock markdown with headers
    mock_files = [FileInfo(path="docs/anchors.md", sha="anchor123", type="blob", size=2048)]
    mock_content = """# Main Title

## Section 1

Content under section 1.

## Section 2

Content under section 2.

### Subsection 2.1

Nested content.

## Section 3

Final section content.
"""

    mock_embedding = [0.1] * 768

    with (
        patch.object(GitHubService, "fetch_repository_tree", new_callable=AsyncMock) as mock_tree,
        patch.object(
            GitHubService, "download_file_content", new_callable=AsyncMock
        ) as mock_download,
        patch.object(
            GitHubService, "get_last_commit_date", new_callable=AsyncMock
        ) as mock_commit_date,
        patch.object(
            EmbeddingService, "generate_embeddings_batch", new_callable=AsyncMock
        ) as mock_embeddings,
    ):

        mock_tree.return_value = mock_files
        mock_download.return_value = (mock_content, "abc123")
        mock_commit_date.return_value = datetime.utcnow()
        mock_embeddings.return_value = [mock_embedding] * 20

        # Initialize services
        project_doc_repo = ProjectDocRepository()
        document_repo = DocumentRepository(db_session)
        document_service = DocumentService(document_repo)
        github_service = GitHubService()
        docling_service = DoclingService()
        embedding_service = EmbeddingService()
        chunk_repository = ChunkRepository(db_session)

        project_doc_service = ProjectDocService(
            project_doc_repo=project_doc_repo,
            github_service=github_service,
            document_service=document_service,
            docling_service=docling_service,
            embedding_service=embedding_service,
            chunk_repository=chunk_repository,
        )

        # Act
        await project_doc_service.sync_project_doc(db_session, test_project_doc.id)

        # Get chunks
        documents = await document_repo.get_by_project_doc_id(test_project_doc.id)
        chunks = await chunk_repository.get_by_document_id(documents[0].id)

        # Count chunks with header anchors
        chunks_with_anchors = sum(1 for chunk in chunks if chunk.header_anchor is not None)
        total_chunks = len(chunks)

        # Assert: >90% have anchors
        anchor_percentage = (chunks_with_anchors / total_chunks) * 100
        assert (
            anchor_percentage > 90
        ), f"Only {anchor_percentage:.1f}% of chunks have anchors (expected >90%)"

        # Verify anchor format (lowercase, hyphens)
        for chunk in chunks:
            if chunk.header_anchor:
                # Anchors should be lowercase with hyphens
                assert chunk.header_anchor.islower() or "-" in chunk.header_anchor
                # No spaces
                assert " " not in chunk.header_anchor
