"""Tests for SyncService."""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.services.sync_service import SyncService, detect_doc_type, extract_title


def test_detect_doc_type_scoping():
    """Test doc type detection for scoping documents."""
    assert detect_doc_type("docs/prd/overview.md") == "scoping"
    assert detect_doc_type("DOCS/PRD/OVERVIEW.MD") == "scoping"


def test_detect_doc_type_architecture():
    """Test doc type detection for architecture documents."""
    assert detect_doc_type("docs/architecture/tech-stack.md") == "architecture"
    assert detect_doc_type("DOCS/ARCHITECTURE/BACKEND.MD") == "architecture"


def test_detect_doc_type_epic():
    """Test doc type detection for epic documents."""
    assert detect_doc_type("docs/epics/epic-1.md") == "epic"
    assert detect_doc_type("DOCS/EPICS/EPIC-2.MD") == "epic"


def test_detect_doc_type_story():
    """Test doc type detection for story documents."""
    assert detect_doc_type("docs/stories/story-1.1.md") == "story"
    assert detect_doc_type("DOCS/STORIES/STORY-2.3.MD") == "story"


def test_detect_doc_type_qa():
    """Test doc type detection for QA documents."""
    assert detect_doc_type("docs/qa/test-plan.md") == "qa"
    assert detect_doc_type("DOCS/QA/TESTING.MD") == "qa"


def test_detect_doc_type_other():
    """Test doc type detection for other documents."""
    assert detect_doc_type("README.md") == "other"
    assert detect_doc_type("src/main.py") == "other"
    assert detect_doc_type("docs/other/notes.md") == "other"


def test_extract_title_from_heading():
    """Test extracting title from markdown heading."""
    content = "# Overview\n\nThis is content."
    assert extract_title(content) == "Overview"


def test_extract_title_from_heading_with_whitespace():
    """Test extracting title from heading with whitespace."""
    content = "#   Spaced Title   \n\nContent here."
    assert extract_title(content) == "Spaced Title"


def test_extract_title_fallback_first_line():
    """Test extracting title fallback to first non-empty line."""
    content = "\n\nFirst non-empty line\nSecond line."
    assert extract_title(content) == "First non-empty line"


def test_extract_title_fallback_untitled():
    """Test extracting title fallback to 'Untitled'."""
    content = ""
    assert extract_title(content) == "Untitled"


def test_extract_title_long_line_truncation():
    """Test extracting title truncates long lines."""
    content = "A" * 600
    result = extract_title(content)
    assert len(result) == 500
    assert result == "A" * 500


@pytest.fixture
def mock_db():
    """Mock async database session."""
    return AsyncMock()


@pytest.fixture
def mock_github_service():
    """Mock GitHub service."""
    with patch("src.services.sync_service.GitHubService") as mock:
        yield mock


@pytest.fixture
def sync_service(mock_db, mock_github_service):
    """Create SyncService with mocked dependencies."""
    with patch("src.services.sync_service.settings") as mock_settings:
        mock_settings.GITHUB_TOKEN = "test-token"
        service = SyncService(mock_db)
        return service


@pytest.mark.asyncio
async def test_sync_project_success(sync_service, mock_db):
    """Test successful project sync."""
    project_id = uuid.uuid4()

    # Mock project repository
    mock_project = MagicMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/owner/repo"

    with patch.object(
        sync_service.project_repo, "get_by_id", return_value=mock_project
    ):
        with patch.object(sync_service.project_repo, "update", new=AsyncMock()):
            with patch.object(
                sync_service.github_service,
                "validate_repo_url",
                return_value=("owner", "repo"),
            ):
                with patch.object(
                    sync_service.github_service,
                    "fetch_all_markdown_files",
                    return_value=[
                        ("docs/prd/overview.md", "# Overview\nContent"),
                        ("docs/architecture/tech-stack.md", "# Tech Stack\nDetails"),
                    ],
                ):
                    with patch.object(
                        sync_service.document_repo, "upsert", new=AsyncMock()
                    ):
                        # Execute
                        result = await sync_service.sync_project(project_id)

                        # Assert
                        assert result["processed_count"] == 2
                        assert result["total_count"] == 2
                        assert len(result["failed_files"]) == 0


@pytest.mark.asyncio
async def test_sync_project_not_found(sync_service):
    """Test sync when project not found."""
    project_id = uuid.uuid4()

    with patch.object(sync_service.project_repo, "get_by_id", return_value=None):
        # Execute and assert
        with pytest.raises(ValueError, match="Project not found"):
            await sync_service.sync_project(project_id)


@pytest.mark.asyncio
async def test_sync_project_partial_failure(sync_service, mock_db):
    """Test sync with partial file failures (>90% success)."""
    project_id = uuid.uuid4()

    # Mock project
    mock_project = MagicMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/owner/repo"

    # Mock 10 files, 1 will fail
    files = [(f"docs/prd/file{i}.md", f"# File {i}\nContent") for i in range(10)]

    call_count = 0

    async def mock_upsert(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 3:  # Fail on 3rd file
            raise Exception("Simulated error")
        return MagicMock()

    with patch.object(
        sync_service.project_repo, "get_by_id", return_value=mock_project
    ):
        with patch.object(sync_service.project_repo, "update", new=AsyncMock()):
            with patch.object(
                sync_service.github_service,
                "validate_repo_url",
                return_value=("owner", "repo"),
            ):
                with patch.object(
                    sync_service.github_service,
                    "fetch_all_markdown_files",
                    return_value=files,
                ):
                    with patch.object(
                        sync_service.document_repo, "upsert", side_effect=mock_upsert
                    ):
                        # Execute
                        result = await sync_service.sync_project(project_id)

                        # Assert - 9/10 files processed (90%), should succeed
                        assert result["processed_count"] == 9
                        assert result["total_count"] == 10
                        assert len(result["failed_files"]) == 1


@pytest.mark.asyncio
async def test_sync_project_major_failure(sync_service, mock_db):
    """Test sync with major failures (<90% success)."""
    project_id = uuid.uuid4()

    # Mock project
    mock_project = MagicMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/owner/repo"

    # Mock 10 files, 6 will fail (60% success < 90%)
    files = [(f"docs/prd/file{i}.md", f"# File {i}\nContent") for i in range(10)]

    call_count = 0

    async def mock_upsert(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > 4:  # Fail on files after 4th
            raise Exception("Simulated error")
        return MagicMock()

    with patch.object(
        sync_service.project_repo, "get_by_id", return_value=mock_project
    ):
        with patch.object(sync_service.project_repo, "update", new=AsyncMock()):
            with patch.object(
                sync_service.github_service,
                "validate_repo_url",
                return_value=("owner", "repo"),
            ):
                with patch.object(
                    sync_service.github_service,
                    "fetch_all_markdown_files",
                    return_value=files,
                ):
                    with patch.object(
                        sync_service.document_repo, "upsert", side_effect=mock_upsert
                    ):
                        # Execute and assert
                        with pytest.raises(ValueError, match="Sync failed"):
                            await sync_service.sync_project(project_id)


@pytest.mark.asyncio
async def test_sync_project_task_tracker_updates(sync_service, mock_db):
    """Test that task tracker is updated during sync."""
    project_id = uuid.uuid4()
    task_tracker = {}

    # Mock project
    mock_project = MagicMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/owner/repo"

    files = [
        ("docs/prd/file1.md", "# File 1"),
        ("docs/prd/file2.md", "# File 2"),
    ]

    with patch.object(
        sync_service.project_repo, "get_by_id", return_value=mock_project
    ):
        with patch.object(sync_service.project_repo, "update", new=AsyncMock()):
            with patch.object(
                sync_service.github_service,
                "validate_repo_url",
                return_value=("owner", "repo"),
            ):
                with patch.object(
                    sync_service.github_service,
                    "fetch_all_markdown_files",
                    return_value=files,
                ):
                    with patch.object(
                        sync_service.document_repo, "upsert", new=AsyncMock()
                    ):
                        # Execute
                        result = await sync_service.sync_project(
                            project_id, task_tracker=task_tracker
                        )

                        # Assert task tracker was updated
                        assert task_tracker["total_count"] == 2
                        assert task_tracker["processed_count"] == 2
                        assert task_tracker["current_file"] == "docs/prd/file2.md"
