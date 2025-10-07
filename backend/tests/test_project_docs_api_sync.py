"""Unit tests for sync API endpoints."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.project_doc import ProjectDoc

client = TestClient(app)


def test_post_sync_endpoint_202():
    """Test POST /project-docs/{id}/sync returns 202 Accepted."""
    project_doc_id = uuid.uuid4()

    # Mock repository to return a project doc
    mock_project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
    )

    with patch("app.routers.project_docs.ProjectDocRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_project_doc
        mock_repo_class.return_value = mock_repo

        response = client.post(f"/api/project-docs/{project_doc_id}/sync")

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["status"] == "processing"
        assert data["project_doc_id"] == str(project_doc_id)
        assert "message" in data


def test_post_sync_endpoint_404():
    """Test POST /project-docs/{id}/sync returns 404 when ProjectDoc not found."""
    project_doc_id = uuid.uuid4()

    with patch("app.routers.project_docs.ProjectDocRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None  # Not found
        mock_repo_class.return_value = mock_repo

        response = client.post(f"/api/project-docs/{project_doc_id}/sync")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()


def test_get_sync_status_idle():
    """Test GET /project-docs/{id}/sync-status returns 'idle' when never synced."""
    project_doc_id = uuid.uuid4()

    mock_project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
        last_synced_at=None,  # Never synced
        last_github_commit_date=None,
    )

    with patch("app.routers.project_docs.ProjectDocRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_project_doc
        mock_repo_class.return_value = mock_repo

        response = client.get(f"/api/project-docs/{project_doc_id}/sync-status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "idle"
        assert "not synced" in data["message"].lower()
        assert data["last_synced_at"] is None


def test_get_sync_status_syncing():
    """Test GET /project-docs/{id}/sync-status returns 'syncing' when recent sync."""
    project_doc_id = uuid.uuid4()

    # Sync happened 2 minutes ago (within 5-minute window)
    recent_sync = datetime.now(timezone.utc) - timedelta(minutes=2)

    mock_project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
        last_synced_at=recent_sync,
        last_github_commit_date=datetime.now(timezone.utc),
    )

    with patch("app.routers.project_docs.ProjectDocRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_project_doc
        mock_repo_class.return_value = mock_repo

        response = client.get(f"/api/project-docs/{project_doc_id}/sync-status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "syncing"
        assert "syncing" in data["message"].lower()


def test_get_sync_status_completed():
    """Test GET /project-docs/{id}/sync-status returns 'completed' with file count."""
    project_doc_id = uuid.uuid4()

    # Sync happened 10 minutes ago (outside 5-minute window)
    old_sync = datetime.now(timezone.utc) - timedelta(minutes=10)

    mock_project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
        last_synced_at=old_sync,
        last_github_commit_date=old_sync - timedelta(hours=1),  # Commit before sync
    )

    with (
        patch("app.routers.project_docs.ProjectDocRepository") as mock_repo_class,
        patch("app.routers.project_docs.DocumentRepository") as mock_doc_repo_class,
    ):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_project_doc
        mock_repo_class.return_value = mock_repo

        mock_doc_repo = AsyncMock()
        mock_doc_repo.count_by_project_doc.return_value = 42  # 42 files
        mock_doc_repo_class.return_value = mock_doc_repo

        response = client.get(f"/api/project-docs/{project_doc_id}/sync-status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert "42 files" in data["message"]
        assert "successfully" in data["message"].lower()


def test_get_sync_status_needs_update():
    """Test sync status message includes 'Needs update' when last_synced_at < last_github_commit_date."""
    project_doc_id = uuid.uuid4()

    # Sync happened before the last commit (needs update)
    old_sync = datetime.now(timezone.utc) - timedelta(hours=2)
    recent_commit = datetime.now(timezone.utc) - timedelta(hours=1)

    mock_project_doc = ProjectDoc(
        id=project_doc_id,
        project_id=uuid.uuid4(),
        name="Test Doc",
        github_url="https://github.com/owner/repo",
        github_folder_path="docs",
        last_synced_at=old_sync,
        last_github_commit_date=recent_commit,  # Commit after sync
    )

    with (
        patch("app.routers.project_docs.ProjectDocRepository") as mock_repo_class,
        patch("app.routers.project_docs.DocumentRepository") as mock_doc_repo_class,
    ):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_project_doc
        mock_repo_class.return_value = mock_repo

        mock_doc_repo = AsyncMock()
        mock_doc_repo.count_by_project_doc.return_value = 10
        mock_doc_repo_class.return_value = mock_doc_repo

        response = client.get(f"/api/project-docs/{project_doc_id}/sync-status")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert "needs update" in data["message"].lower()


def test_get_sync_status_404():
    """Test GET /project-docs/{id}/sync-status returns 404 when ProjectDoc not found."""
    project_doc_id = uuid.uuid4()

    with patch("app.routers.project_docs.ProjectDocRepository") as mock_repo_class:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None  # Not found
        mock_repo_class.return_value = mock_repo

        response = client.get(f"/api/project-docs/{project_doc_id}/sync-status")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"].lower()
