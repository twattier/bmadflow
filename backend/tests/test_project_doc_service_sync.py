"""Unit tests for ProjectDocService sync orchestration."""

import time
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import GitHubAPIError
from app.models.project_doc import ProjectDoc
from app.schemas.github import FileInfo
from app.services.document_service import DocumentService
from app.services.github_service import GitHubService
from app.services.project_doc_service import ProjectDocService


@pytest.mark.asyncio
async def test_sync_project_doc_success():
    """Test successful sync workflow."""
    # Arrange
    project_doc_id = uuid.uuid4()
    project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = project_doc

    mock_github = AsyncMock(spec=GitHubService)
    mock_github.fetch_repository_tree.return_value = [
        FileInfo(path="docs/prd.md", sha="abc123", type="blob"),
        FileInfo(path="docs/arch.md", sha="def456", type="blob"),
    ]
    mock_github.download_file_content.return_value = ("# Content", "abc123")
    mock_github.get_last_commit_date.return_value = datetime(2025, 1, 15, 10, 30)

    mock_doc_service = AsyncMock(spec=DocumentService)
    mock_doc_service.store_documents_batch.return_value = [
        MagicMock(id=uuid.uuid4()),
        MagicMock(id=uuid.uuid4()),
    ]

    mock_db = AsyncMock()
    service = ProjectDocService(mock_repo, mock_github, mock_doc_service)

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is True
    assert result.files_synced == 2
    assert result.files_failed == 0
    assert len(result.errors) == 0
    assert result.duration_seconds > 0
    mock_github.fetch_repository_tree.assert_called_once()
    mock_doc_service.store_documents_batch.assert_called_once()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_sync_project_doc_updates_timestamps():
    """Test that last_synced_at and last_github_commit_date are updated."""
    # Arrange
    project_doc_id = uuid.uuid4()
    project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = project_doc

    mock_github = AsyncMock(spec=GitHubService)
    mock_github.fetch_repository_tree.return_value = []
    expected_commit_date = datetime(2025, 1, 15, 10, 30)
    mock_github.get_last_commit_date.return_value = expected_commit_date

    mock_doc_service = AsyncMock(spec=DocumentService)
    mock_doc_service.store_documents_batch.return_value = []

    mock_db = AsyncMock()
    service = ProjectDocService(mock_repo, mock_github, mock_doc_service)

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is True
    assert project_doc.last_synced_at is not None
    assert project_doc.last_github_commit_date == expected_commit_date
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_sync_project_doc_handles_github_errors():
    """Test error handling when GitHub API fails."""
    # Arrange
    project_doc_id = uuid.uuid4()
    project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = project_doc

    mock_github = AsyncMock(spec=GitHubService)
    mock_github.fetch_repository_tree.side_effect = GitHubAPIError("Rate limit exceeded", 403)

    mock_doc_service = AsyncMock(spec=DocumentService)

    mock_db = AsyncMock()
    service = ProjectDocService(mock_repo, mock_github, mock_doc_service)

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is False
    assert result.files_synced == 0
    assert len(result.errors) > 0
    assert "Rate limit exceeded" in result.errors[0]


@pytest.mark.asyncio
async def test_sync_project_doc_partial_failure():
    """Test sync continues when individual files fail."""
    # Arrange
    project_doc_id = uuid.uuid4()
    project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = project_doc

    mock_github = AsyncMock(spec=GitHubService)
    mock_github.fetch_repository_tree.return_value = [
        FileInfo(path="docs/file1.md", sha="abc123", type="blob"),
        FileInfo(path="docs/file2.md", sha="def456", type="blob"),
        FileInfo(path="docs/file3.md", sha="ghi789", type="blob"),
        FileInfo(path="docs/file4.md", sha="jkl012", type="blob"),
        FileInfo(path="docs/file5.md", sha="mno345", type="blob"),
    ]

    # Simulate 2 download failures
    def download_side_effect(url, path):
        if "file2" in path or "file4" in path:
            raise GitHubAPIError(f"Failed to download {path}", 404)
        return ("# Content", "abc123")

    mock_github.download_file_content.side_effect = download_side_effect
    mock_github.get_last_commit_date.return_value = datetime(2025, 1, 15, 10, 30)

    mock_doc_service = AsyncMock(spec=DocumentService)
    mock_doc_service.store_documents_batch.return_value = [
        MagicMock(id=uuid.uuid4()),
        MagicMock(id=uuid.uuid4()),
        MagicMock(id=uuid.uuid4()),
    ]

    mock_db = AsyncMock()
    service = ProjectDocService(mock_repo, mock_github, mock_doc_service)

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is True  # Overall success even with partial failures
    assert result.files_synced == 3  # 3 files successfully stored
    assert result.files_failed == 2  # 2 files failed
    assert len(result.errors) == 2


@pytest.mark.asyncio
@pytest.mark.respx(base_url="https://api.github.com")
async def test_get_last_commit_date_success(respx_mock):
    """Test successful last commit date fetching."""
    # Arrange
    respx_mock.get("/repos/owner/repo/commits").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "sha": "abc123",
                    "commit": {
                        "committer": {"date": "2025-01-15T10:30:00Z"},
                    },
                }
            ],
            headers={
                "X-RateLimit-Remaining": "4999",
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Reset": str(int(time.time()) + 3600),
            },
        )
    )

    service = GitHubService()

    # Act
    commit_date = await service.get_last_commit_date("https://github.com/owner/repo", "docs")

    # Assert
    assert commit_date.year == 2025
    assert commit_date.month == 1
    assert commit_date.day == 15
    assert commit_date.hour == 10
    assert commit_date.minute == 30


@pytest.mark.asyncio
async def test_get_last_commit_date_404():
    """Test 404 error when folder not found."""
    # Arrange
    mock_response = httpx.Response(404, json={"message": "Not Found"})
    mock_response.raise_for_status = lambda: None  # Don't raise on construction

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get.return_value = mock_response

        # Simulate raise_for_status raising HTTPStatusError
        def raise_for_status():
            raise httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=mock_response
            )

        mock_response.raise_for_status = raise_for_status

        service = GitHubService()

        # Act & Assert
        with pytest.raises(GitHubAPIError) as exc_info:
            await service.get_last_commit_date("https://github.com/owner/repo", "nonexistent")

        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_sync_project_doc_not_found():
    """Test sync fails gracefully when ProjectDoc not found."""
    # Arrange
    project_doc_id = uuid.uuid4()

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None

    mock_github = AsyncMock(spec=GitHubService)
    mock_doc_service = AsyncMock(spec=DocumentService)

    mock_db = AsyncMock()
    service = ProjectDocService(mock_repo, mock_github, mock_doc_service)

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is False
    assert "not found" in result.errors[0].lower()
    assert result.files_synced == 0


@pytest.mark.asyncio
async def test_sync_project_doc_timezone_aware_timestamps():
    """Test that timestamps are timezone-aware and properly comparable."""
    # Arrange
    project_doc_id = uuid.uuid4()
    project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = project_doc

    mock_github = AsyncMock(spec=GitHubService)
    mock_github.fetch_repository_tree.return_value = []

    # Return timezone-aware datetime from GitHub API (like real implementation)
    from datetime import timezone

    expected_commit_date = datetime(2025, 1, 15, 10, 30, tzinfo=timezone.utc)
    mock_github.get_last_commit_date.return_value = expected_commit_date

    mock_doc_service = AsyncMock(spec=DocumentService)
    mock_doc_service.store_documents_batch.return_value = []

    mock_db = AsyncMock()
    service = ProjectDocService(mock_repo, mock_github, mock_doc_service)

    # Act
    result = await service.sync_project_doc(mock_db, project_doc_id)

    # Assert
    assert result.success is True

    # Verify timestamps are timezone-aware
    assert project_doc.last_synced_at is not None
    assert project_doc.last_synced_at.tzinfo is not None, "last_synced_at must be timezone-aware"
    assert (
        project_doc.last_github_commit_date.tzinfo is not None
    ), "last_github_commit_date must be timezone-aware"

    # Verify comparison works correctly (both are timezone-aware)
    # last_synced_at should be >= last_github_commit_date (sync happened after last commit)
    assert (
        project_doc.last_synced_at >= project_doc.last_github_commit_date
    ), "last_synced_at should be after or equal to last_github_commit_date"


import httpx
