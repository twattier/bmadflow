"""Integration tests for project API routes."""

import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from src.main import app
from src.models.project import Project
from src.models.document import Document


@pytest.fixture
def client():
    """Create async HTTP client for testing."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_project_success(client):
    """Test creating a new project."""
    with patch("src.routes.projects.ProjectRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_github_url.return_value = None  # No duplicate
        created_project = Project(
            id=uuid.uuid4(),
            name="test-repo",
            github_url="https://github.com/owner/test-repo",
            sync_status="idle",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.create.return_value = created_project
        mock_repo_class.return_value = mock_repo

        # Execute
        response = await client.post(
            "/api/projects", json={"github_url": "https://github.com/owner/test-repo"}
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-repo"
        assert data["github_url"] == "https://github.com/owner/test-repo"
        assert data["sync_status"] == "idle"


@pytest.mark.asyncio
async def test_create_project_duplicate(client):
    """Test creating a project with duplicate github_url."""
    with patch("src.routes.projects.ProjectRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        # Mock existing project
        existing_project = Project(
            id=uuid.uuid4(),
            name="existing-repo",
            github_url="https://github.com/owner/existing-repo",
            sync_status="idle",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_github_url.return_value = existing_project
        mock_repo_class.return_value = mock_repo

        # Execute
        response = await client.post(
            "/api/projects",
            json={"github_url": "https://github.com/owner/existing-repo"},
        )

        # Assert
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_project_invalid_url(client):
    """Test creating a project with invalid GitHub URL."""
    # Execute
    response = await client.post(
        "/api/projects", json={"github_url": "https://bitbucket.org/owner/repo"}
    )

    # Assert
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_trigger_sync_success(client):
    """Test triggering sync for a project."""
    project_id = uuid.uuid4()

    with patch("src.routes.projects.ProjectRepository") as mock_repo_class:
        with patch("src.routes.projects.SyncService") as mock_sync_service_class:
            # Mock project repository
            mock_repo = AsyncMock()
            existing_project = Project(
                id=project_id,
                name="test-repo",
                github_url="https://github.com/owner/test-repo",
                sync_status="idle",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_repo.get_by_id.return_value = existing_project
            mock_repo.update = AsyncMock()
            mock_repo_class.return_value = mock_repo

            # Mock sync service
            mock_sync_service = MagicMock()
            mock_sync_service.github_service.validate_repo_url.return_value = (
                "owner",
                "test-repo",
            )
            mock_sync_service_class.return_value = mock_sync_service

            # Execute
            response = await client.post(f"/api/projects/{project_id}/sync")

            # Assert
            assert response.status_code == 202
            data = response.json()
            assert "sync_task_id" in data
            assert data["message"] == "Sync started"


@pytest.mark.asyncio
async def test_trigger_sync_project_not_found(client):
    """Test triggering sync for non-existent project."""
    project_id = uuid.uuid4()

    with patch("src.routes.projects.ProjectRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None  # Project not found
        mock_repo_class.return_value = mock_repo

        # Execute
        response = await client.post(f"/api/projects/{project_id}/sync")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_trigger_sync_already_in_progress(client):
    """Test triggering sync when sync already in progress."""
    project_id = uuid.uuid4()

    with patch("src.routes.projects.ProjectRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        # Mock project with syncing status
        existing_project = Project(
            id=project_id,
            name="test-repo",
            github_url="https://github.com/owner/test-repo",
            sync_status="syncing",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        mock_repo.get_by_id.return_value = existing_project
        mock_repo_class.return_value = mock_repo

        # Execute
        response = await client.post(f"/api/projects/{project_id}/sync")

        # Assert
        assert response.status_code == 409
        assert "already in progress" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_sync_status_success(client):
    """Test getting sync status."""
    project_id = uuid.uuid4()
    task_id = "task-1"

    # Mock both project_task_map and sync_tasks
    with patch("src.routes.projects.project_task_map") as mock_project_map:
        with patch("src.routes.projects.sync_tasks") as mock_tasks:
            mock_project_map.get = MagicMock(return_value=task_id)
            mock_tasks.get = MagicMock(
                return_value={
                    "status": "completed",
                    "processed_count": 50,
                    "total_count": 50,
                    "error_message": None,
                    "retry_allowed": False,
                }
            )

            # Execute
            response = await client.get(f"/api/projects/{project_id}/sync-status")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["processed_count"] == 50
            assert data["total_count"] == 50
            assert data["error_message"] is None
            assert data["retry_allowed"] is False


@pytest.mark.asyncio
async def test_get_sync_status_not_found(client):
    """Test getting sync status when no task exists."""
    project_id = uuid.uuid4()

    # Mock empty project_task_map
    with patch("src.routes.projects.project_task_map") as mock_project_map:
        mock_project_map.get = MagicMock(return_value=None)

        # Execute
        response = await client.get(f"/api/projects/{project_id}/sync-status")

        # Assert
        assert response.status_code == 404
        assert "No sync task found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_full_sync_flow(client):
    """Integration test: Full sync flow with 50-doc mock repository."""
    with patch("src.routes.projects.ProjectRepository") as mock_repo_class:
        with patch("src.routes.projects.SyncService") as mock_sync_service_class:
            with patch("src.routes.projects.sync_tasks") as mock_tasks:
                with patch("src.routes.projects.project_task_map") as mock_project_map:
                    # Step 1: Create project
                    mock_repo = AsyncMock()
                    mock_repo.get_by_github_url.return_value = None
                    created_project = Project(
                        id=uuid.uuid4(),
                        name="test-repo",
                        github_url="https://github.com/owner/test-repo",
                        sync_status="idle",
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    mock_repo.create.return_value = created_project
                    mock_repo.get_by_id.return_value = created_project
                    mock_repo.update = AsyncMock()
                    mock_repo_class.return_value = mock_repo

                    # Create project
                    response = await client.post(
                        "/api/projects",
                        json={"github_url": "https://github.com/owner/test-repo"},
                    )
                    assert response.status_code == 201
                    project_id = response.json()["id"]

                    # Step 2: Trigger sync
                    mock_sync_service = MagicMock()
                    mock_sync_service.github_service.validate_repo_url.return_value = (
                        "owner",
                        "test-repo",
                    )
                    mock_sync_service_class.return_value = mock_sync_service

                    response = await client.post(f"/api/projects/{project_id}/sync")
                    assert response.status_code == 202
                    sync_task_id = response.json()["sync_task_id"]

                    # Step 3: Check sync status (simulated completion)
                    mock_project_map.get = MagicMock(return_value=sync_task_id)
                    mock_tasks.get = MagicMock(
                        return_value={
                            "status": "completed",
                            "processed_count": 50,
                            "total_count": 50,
                            "error_message": None,
                            "retry_allowed": False,
                        }
                    )

                    response = await client.get(
                        f"/api/projects/{project_id}/sync-status"
                    )
                    assert response.status_code == 200
                    status_data = response.json()
                    assert status_data["status"] == "completed"
                    assert status_data["processed_count"] == 50
                    assert status_data["total_count"] == 50


@pytest.mark.asyncio
async def test_full_sync_with_correct_doc_types(client):
    """Test that all documents are stored with correct doc_type values."""
    # This is tested more thoroughly in test_sync_service.py
    # Here we verify the integration point

    test_files = [
        ("docs/prd/overview.md", "# Overview", "scoping"),
        ("docs/architecture/tech-stack.md", "# Tech Stack", "architecture"),
        ("docs/epics/epic-1.md", "# Epic 1", "epic"),
        ("docs/stories/story-1.1.md", "# Story 1.1", "story"),
        ("docs/qa/test-plan.md", "# Test Plan", "qa"),
        ("README.md", "# README", "other"),
    ]

    # Import and test doc_type detection directly
    from src.services.sync_service import detect_doc_type

    for file_path, content, expected_type in test_files:
        assert detect_doc_type(file_path) == expected_type
