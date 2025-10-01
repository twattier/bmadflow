"""Tests for ProjectRepository."""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.repositories.project_repository import ProjectRepository
from src.models.project import Project


@pytest.fixture
def mock_db():
    """Mock async database session."""
    db = AsyncMock()
    return db


@pytest.fixture
def project_repo(mock_db):
    """Create ProjectRepository with mocked database."""
    return ProjectRepository(mock_db)


@pytest.mark.asyncio
async def test_get_by_id(project_repo, mock_db):
    """Test getting project by ID."""
    project_id = uuid.uuid4()
    expected_project = Project(
        id=project_id,
        name="test-repo",
        github_url="https://github.com/owner/test-repo",
        sync_status="idle",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Mock database result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_project
    mock_db.execute.return_value = mock_result

    # Execute
    result = await project_repo.get_by_id(project_id)

    # Assert
    assert result == expected_project
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(project_repo, mock_db):
    """Test getting project by ID when not found."""
    project_id = uuid.uuid4()

    # Mock database result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Execute
    result = await project_repo.get_by_id(project_id)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_create(project_repo, mock_db):
    """Test creating a project."""
    project_data = {
        "name": "new-repo",
        "github_url": "https://github.com/owner/new-repo",
        "sync_status": "idle",
    }

    # Mock the created project
    created_project = Project(id=uuid.uuid4(), **project_data)

    # Mock database operations
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    with patch.object(Project, "__init__", return_value=None):
        # Execute
        result = await project_repo.create(**project_data)

        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update(project_repo, mock_db):
    """Test updating a project."""
    project_id = uuid.uuid4()
    existing_project = Project(
        id=project_id,
        name="test-repo",
        github_url="https://github.com/owner/test-repo",
        sync_status="idle",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Mock get_by_id
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_project
    mock_db.execute.return_value = mock_result

    # Mock database operations
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    # Execute
    result = await project_repo.update(project_id, sync_status="syncing")

    # Assert
    assert existing_project.sync_status == "syncing"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_github_url(project_repo, mock_db):
    """Test getting project by GitHub URL."""
    github_url = "https://github.com/owner/test-repo"
    expected_project = Project(
        id=uuid.uuid4(),
        name="test-repo",
        github_url=github_url,
        sync_status="idle",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Mock database result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_project
    mock_db.execute.return_value = mock_result

    # Execute
    result = await project_repo.get_by_github_url(github_url)

    # Assert
    assert result == expected_project
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_github_url_not_found(project_repo, mock_db):
    """Test getting project by GitHub URL when not found."""
    github_url = "https://github.com/owner/nonexistent"

    # Mock database result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Execute
    result = await project_repo.get_by_github_url(github_url)

    # Assert
    assert result is None
