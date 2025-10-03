"""End-to-end integration tests for sync + extraction pipeline (Story 2.5)."""

import pytest
import uuid
from unittest.mock import AsyncMock, patch
from src.services.sync_service import SyncService


@pytest.fixture
def mock_db():
    """Mock async database session."""
    return AsyncMock()


@pytest.fixture
def sample_story_markdown():
    """Sample story markdown content."""
    return """# Story 1.1: User Authentication

## Status

Dev

## Story

**As a** user,
**I want** to log in with GitHub OAuth,
**so that** I can access the platform securely.

## Acceptance Criteria

1. User can click "Sign in with GitHub" button
2. OAuth flow redirects to GitHub for authentication
3. User is redirected back with access token
4. Token is stored securely in httpOnly cookie

## Tasks / Subtasks

- [x] Task 1: Set up GitHub OAuth app
- [x] Task 2: Implement OAuth callback endpoint
- [ ] Task 3: Add token storage
"""


@pytest.fixture
def sample_epic_markdown():
    """Sample epic markdown content."""
    return """# Epic 1: Authentication System

## Epic Goal

Implement secure user authentication using GitHub OAuth to enable user-specific functionality.

## Epic Description

This epic delivers the authentication infrastructure for BMADFlow.

## Stories

- [Story 1.1](stories/story-1-1.md): User Authentication
- [Story 1.2](stories/story-1-2.md): Session Management
"""


@pytest.fixture
def mock_github_files(sample_story_markdown, sample_epic_markdown):
    """Mock GitHub files for testing."""
    return [
        ("docs/stories/story-1-1-user-auth.md", sample_story_markdown),
        ("docs/stories/story-1-2-session.md", sample_story_markdown),  # Reuse content
        ("docs/epics/epic-1-auth.md", sample_epic_markdown),
        ("docs/epics/epic-2-data.md", sample_epic_markdown),  # Reuse content
        ("docs/architecture/tech-stack.md", "# Tech Stack\n\nPython, React"),  # Won't be extracted
    ]


@pytest.mark.asyncio
async def test_sync_triggers_extraction_for_epics_and_stories(mock_db, mock_github_files):
    """Test that sync automatically extracts epic and story documents.

    AC 1, 2: Sync process extended to trigger extraction for epic/story doc types
    """
    # Setup mocks
    project_id = uuid.uuid4()
    mock_project = AsyncMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/test/repo"

    # Mock project repository
    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = mock_project
    mock_project_repo.update = AsyncMock()

    # Mock document repository
    mock_document_repo = AsyncMock()
    mock_document_repo.upsert = AsyncMock()

    # Create mock documents (stored after sync)
    mock_stored_docs = []
    for file_path, content in mock_github_files:
        mock_doc = AsyncMock()
        mock_doc.id = uuid.uuid4()
        mock_doc.file_path = file_path
        mock_doc.content = content

        # Detect doc type
        if "stories/" in file_path:
            mock_doc.doc_type = "story"
        elif "epics/" in file_path:
            mock_doc.doc_type = "epic"
        else:
            mock_doc.doc_type = "architecture"

        mock_stored_docs.append(mock_doc)

    mock_document_repo.get_by_project_id.return_value = mock_stored_docs

    # Mock extraction services
    mock_story_service = AsyncMock()
    mock_epic_service = AsyncMock()

    # Mock extraction results
    mock_story_result = AsyncMock()
    mock_story_result.confidence_score = 0.95
    mock_story_service.extract_story.return_value = mock_story_result

    mock_epic_result = AsyncMock()
    mock_epic_result.confidence_score = 0.92
    mock_epic_service.extract_epic.return_value = mock_epic_result

    # Mock repositories
    mock_extracted_story_repo = AsyncMock()
    mock_extracted_epic_repo = AsyncMock()

    # Create sync service with all mocks
    with patch("src.services.sync_service.settings") as mock_settings, \
         patch("src.services.sync_service.GitHubService") as MockGitHub, \
         patch("src.services.sync_service.ProjectRepository", return_value=mock_project_repo), \
         patch("src.services.sync_service.DocumentRepository", return_value=mock_document_repo), \
         patch("src.services.sync_service.StoryExtractionService", return_value=mock_story_service), \
         patch("src.services.sync_service.EpicExtractionService", return_value=mock_epic_service), \
         patch("src.services.sync_service.ExtractedStoryRepository", return_value=mock_extracted_story_repo), \
         patch("src.services.sync_service.ExtractedEpicRepository", return_value=mock_extracted_epic_repo):

        mock_settings.GITHUB_TOKEN = "test-token"

        # Mock GitHub service methods
        mock_github_instance = MockGitHub.return_value
        mock_github_instance.validate_repo_url.return_value = ("test", "repo")
        mock_github_instance.fetch_all_markdown_files.return_value = mock_github_files

        service = SyncService(mock_db)

        # Execute sync
        result = await service.sync_project(project_id)

        # Assertions
        assert "extraction_summary" in result, "Result should include extraction_summary"

        summary = result["extraction_summary"]
        assert summary["total_documents"] == 4, "Should have 4 extractable docs (2 stories + 2 epics)"
        assert summary["successfully_extracted"] == 4, "All 4 docs should be extracted successfully"
        assert summary["extraction_failures"] == 0, "No extraction failures expected"
        assert summary["average_confidence_score"] > 0.9, "Average confidence should be > 0.9"

        # Verify extraction services were called for each doc type
        assert mock_story_service.extract_story.call_count == 2, "Should extract 2 stories"
        assert mock_epic_service.extract_epic.call_count == 2, "Should extract 2 epics"


@pytest.mark.asyncio
async def test_extraction_failures_dont_fail_sync(mock_db, mock_github_files):
    """Test that extraction failures are logged but don't fail the entire sync.

    AC 4, 5: Graceful error handling - extraction failures don't fail sync
    """
    project_id = uuid.uuid4()
    mock_project = AsyncMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/test/repo"

    # Mock repositories
    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = mock_project
    mock_project_repo.update = AsyncMock()

    mock_document_repo = AsyncMock()
    mock_document_repo.upsert = AsyncMock()

    # Create mock documents
    mock_story_doc = AsyncMock()
    mock_story_doc.id = uuid.uuid4()
    mock_story_doc.file_path = "docs/stories/story-1.md"
    mock_story_doc.content = "# Story"
    mock_story_doc.doc_type = "story"

    mock_epic_doc = AsyncMock()
    mock_epic_doc.id = uuid.uuid4()
    mock_epic_doc.file_path = "docs/epics/epic-1.md"
    mock_epic_doc.content = "# Epic"
    mock_epic_doc.doc_type = "epic"

    mock_document_repo.get_by_project_id.return_value = [mock_story_doc, mock_epic_doc]

    # Mock extraction services - story fails, epic succeeds
    mock_story_service = AsyncMock()
    mock_story_service.extract_story.side_effect = Exception("Extraction failed - invalid format")

    mock_epic_service = AsyncMock()
    mock_epic_result = AsyncMock()
    mock_epic_result.confidence_score = 0.88
    mock_epic_service.extract_epic.return_value = mock_epic_result

    # Create sync service
    with patch("src.services.sync_service.settings") as mock_settings, \
         patch("src.services.sync_service.GitHubService") as MockGitHub, \
         patch("src.services.sync_service.ProjectRepository", return_value=mock_project_repo), \
         patch("src.services.sync_service.DocumentRepository", return_value=mock_document_repo), \
         patch("src.services.sync_service.StoryExtractionService", return_value=mock_story_service), \
         patch("src.services.sync_service.EpicExtractionService", return_value=mock_epic_service), \
         patch("src.services.sync_service.ExtractedStoryRepository", return_value=AsyncMock()), \
         patch("src.services.sync_service.ExtractedEpicRepository", return_value=AsyncMock()):

        mock_settings.GITHUB_TOKEN = "test-token"

        mock_github_instance = MockGitHub.return_value
        mock_github_instance.validate_repo_url.return_value = ("test", "repo")
        mock_github_instance.fetch_all_markdown_files.return_value = [
            ("docs/stories/story-1.md", "# Story"),
            ("docs/epics/epic-1.md", "# Epic"),
        ]

        service = SyncService(mock_db)

        # Execute sync - should NOT raise exception despite extraction failure
        result = await service.sync_project(project_id)

        # Assertions
        assert "extraction_summary" in result

        summary = result["extraction_summary"]
        assert summary["total_documents"] == 2, "Should have 2 extractable docs"
        assert summary["successfully_extracted"] == 1, "Only 1 doc should extract successfully (epic)"
        assert summary["extraction_failures"] == 1, "Should have 1 extraction failure (story)"

        # Verify project status was updated to idle (not error)
        assert mock_project_repo.update.call_count >= 2, "Project should be updated (syncing → idle)"


@pytest.mark.asyncio
async def test_extraction_progress_tracked_in_task_tracker(mock_db):
    """Test that extraction progress is tracked in task_tracker dict.

    AC 4: Sync status endpoint shows extraction progress
    """
    project_id = uuid.uuid4()
    mock_project = AsyncMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/test/repo"

    task_tracker = {
        "status": "in_progress",
        "processed_count": 0,
        "total_count": 0,
    }

    # Mock repositories
    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = mock_project
    mock_project_repo.update = AsyncMock()

    mock_document_repo = AsyncMock()
    mock_document_repo.upsert = AsyncMock()

    # Create mock story document
    mock_story_doc = AsyncMock()
    mock_story_doc.id = uuid.uuid4()
    mock_story_doc.file_path = "docs/stories/story-1.md"
    mock_story_doc.content = "# Story"
    mock_story_doc.doc_type = "story"

    mock_document_repo.get_by_project_id.return_value = [mock_story_doc]

    # Mock extraction service
    mock_story_service = AsyncMock()
    mock_result = AsyncMock()
    mock_result.confidence_score = 0.95
    mock_story_service.extract_story.return_value = mock_result

    # Create sync service
    with patch("src.services.sync_service.settings") as mock_settings, \
         patch("src.services.sync_service.GitHubService") as MockGitHub, \
         patch("src.services.sync_service.ProjectRepository", return_value=mock_project_repo), \
         patch("src.services.sync_service.DocumentRepository", return_value=mock_document_repo), \
         patch("src.services.sync_service.StoryExtractionService", return_value=mock_story_service), \
         patch("src.services.sync_service.EpicExtractionService", return_value=AsyncMock()), \
         patch("src.services.sync_service.ExtractedStoryRepository", return_value=AsyncMock()), \
         patch("src.services.sync_service.ExtractedEpicRepository", return_value=AsyncMock()):

        mock_settings.GITHUB_TOKEN = "test-token"

        mock_github_instance = MockGitHub.return_value
        mock_github_instance.validate_repo_url.return_value = ("test", "repo")
        mock_github_instance.fetch_all_markdown_files.return_value = [
            ("docs/stories/story-1.md", "# Story"),
        ]

        service = SyncService(mock_db)

        # Execute sync with task_tracker
        result = await service.sync_project(project_id, task_tracker=task_tracker)

        # Assertions - task_tracker should be updated with extraction metrics
        assert "extraction_phase" in task_tracker, "task_tracker should include extraction_phase"
        assert task_tracker["extraction_phase"] == "completed", "Extraction phase should be completed"
        assert task_tracker["extracted_count"] == 1, "Should have extracted 1 document"
        assert task_tracker["extraction_failures"] == 0, "Should have 0 extraction failures"


@pytest.mark.asyncio
async def test_concurrent_extraction_uses_semaphore(mock_db):
    """Test that extraction processes documents concurrently with semaphore limit.

    AC 3: Extraction parallelized - process 4 documents concurrently
    """
    project_id = uuid.uuid4()
    mock_project = AsyncMock()
    mock_project.id = project_id
    mock_project.github_url = "https://github.com/test/repo"

    # Mock repositories
    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = mock_project
    mock_project_repo.update = AsyncMock()

    mock_document_repo = AsyncMock()
    mock_document_repo.upsert = AsyncMock()

    # Create 10 mock story documents to test concurrency
    mock_docs = []
    for i in range(10):
        mock_doc = AsyncMock()
        mock_doc.id = uuid.uuid4()
        mock_doc.file_path = f"docs/stories/story-{i}.md"
        mock_doc.content = f"# Story {i}"
        mock_doc.doc_type = "story"
        mock_docs.append(mock_doc)

    mock_document_repo.get_by_project_id.return_value = mock_docs

    # Mock extraction service
    mock_story_service = AsyncMock()
    mock_result = AsyncMock()
    mock_result.confidence_score = 0.90
    mock_story_service.extract_story.return_value = mock_result

    # Create sync service
    with patch("src.services.sync_service.settings") as mock_settings, \
         patch("src.services.sync_service.GitHubService") as MockGitHub, \
         patch("src.services.sync_service.ProjectRepository", return_value=mock_project_repo), \
         patch("src.services.sync_service.DocumentRepository", return_value=mock_document_repo), \
         patch("src.services.sync_service.StoryExtractionService", return_value=mock_story_service), \
         patch("src.services.sync_service.EpicExtractionService", return_value=AsyncMock()), \
         patch("src.services.sync_service.ExtractedStoryRepository", return_value=AsyncMock()), \
         patch("src.services.sync_service.ExtractedEpicRepository", return_value=AsyncMock()):

        mock_settings.GITHUB_TOKEN = "test-token"

        mock_github_instance = MockGitHub.return_value
        mock_github_instance.validate_repo_url.return_value = ("test", "repo")
        mock_github_instance.fetch_all_markdown_files.return_value = [
            (f"docs/stories/story-{i}.md", f"# Story {i}") for i in range(10)
        ]

        service = SyncService(mock_db)

        # Execute sync
        result = await service.sync_project(project_id)

        # Assertions
        assert result["extraction_summary"]["successfully_extracted"] == 10, "All 10 stories should be extracted"
        assert mock_story_service.extract_story.call_count == 10, "Should call extract_story 10 times"

        # Note: In real implementation, semaphore limits to 4 concurrent
        # This test verifies all documents are processed, not the semaphore mechanism directly
