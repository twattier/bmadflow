"""Unit tests for Project API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.routers.projects import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from app.schemas.project import ProjectCreate, ProjectUpdate


@pytest.mark.asyncio
async def test_create_project_success():
    """Test creating project with valid data succeeds."""
    # Arrange
    mock_db = AsyncMock()
    project_data = ProjectCreate(name="Test Project", description="Test Description")
    project_id = uuid4()

    # Create a proper mock that behaves like a Project instance
    expected_project = MagicMock()
    expected_project.id = project_id
    expected_project.name = "Test Project"
    expected_project.description = "Test Description"
    expected_project.created_at = datetime.utcnow()
    expected_project.updated_at = datetime.utcnow()

    # Mock the repository
    import app.routers.projects as projects_module

    original_repo = projects_module.repo
    mock_repo = AsyncMock()
    mock_repo.create.return_value = expected_project
    projects_module.repo = mock_repo

    try:
        # Act
        result = await create_project(project_data, mock_db)

        # Assert
        assert result == expected_project
        mock_repo.create.assert_called_once_with(mock_db, project_data)
    finally:
        # Restore original repo
        projects_module.repo = original_repo


@pytest.mark.asyncio
async def test_list_projects_returns_all_ordered():
    """Test list projects returns all projects ordered by created_at DESC."""
    # Arrange
    mock_db = AsyncMock()
    project1 = MagicMock()
    project1.id = uuid4()
    project1.name = "Project 2"
    project1.created_at = datetime(2025, 10, 7, 12, 0, 0)
    project1.updated_at = datetime(2025, 10, 7, 12, 0, 0)

    project2 = MagicMock()
    project2.id = uuid4()
    project2.name = "Project 1"
    project2.created_at = datetime(2025, 10, 6, 12, 0, 0)
    project2.updated_at = datetime(2025, 10, 6, 12, 0, 0)

    expected_projects = [project1, project2]

    import app.routers.projects as projects_module

    original_repo = projects_module.repo
    mock_repo = AsyncMock()
    mock_repo.get_all.return_value = expected_projects
    projects_module.repo = mock_repo

    try:
        # Act
        result = await list_projects(mock_db)

        # Assert
        assert len(result) == 2
        assert result == expected_projects
        mock_repo.get_all.assert_called_once_with(mock_db)
    finally:
        projects_module.repo = original_repo


@pytest.mark.asyncio
async def test_get_project_by_id_returns_correct_project():
    """Test get project by ID returns correct project."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid4()

    expected_project = MagicMock()
    expected_project.id = project_id
    expected_project.name = "Test Project"
    expected_project.description = "Test"
    expected_project.created_at = datetime.utcnow()
    expected_project.updated_at = datetime.utcnow()

    import app.routers.projects as projects_module

    original_repo = projects_module.repo
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = expected_project
    projects_module.repo = mock_repo

    try:
        # Act
        result = await get_project(project_id, mock_db)

        # Assert
        assert result == expected_project
        mock_repo.get_by_id.assert_called_once_with(mock_db, project_id)
    finally:
        projects_module.repo = original_repo


@pytest.mark.asyncio
async def test_get_project_with_invalid_id_returns_404():
    """Test get project with invalid ID returns 404."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid4()

    import app.routers.projects as projects_module

    original_repo = projects_module.repo
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None
    projects_module.repo = mock_repo

    try:
        # Act & Assert
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_project(project_id, mock_db)

        assert exc_info.value.status_code == 404
        assert str(project_id) in exc_info.value.detail
    finally:
        projects_module.repo = original_repo


@pytest.mark.asyncio
async def test_update_project_modifies_fields():
    """Test update project modifies name and description."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid4()
    update_data = ProjectUpdate(name="Updated Name", description="Updated Desc")

    expected_project = MagicMock()
    expected_project.id = project_id
    expected_project.name = "Updated Name"
    expected_project.description = "Updated Desc"
    expected_project.created_at = datetime(2025, 10, 6, 12, 0, 0)
    expected_project.updated_at = datetime(2025, 10, 7, 12, 0, 0)

    import app.routers.projects as projects_module

    original_repo = projects_module.repo
    mock_repo = AsyncMock()
    mock_repo.update.return_value = expected_project
    projects_module.repo = mock_repo

    try:
        # Act
        result = await update_project(project_id, update_data, mock_db)

        # Assert
        assert result == expected_project
        mock_repo.update.assert_called_once_with(mock_db, project_id, update_data)
    finally:
        projects_module.repo = original_repo


@pytest.mark.asyncio
async def test_delete_project_returns_204():
    """Test delete project returns 204."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid4()

    import app.routers.projects as projects_module

    original_repo = projects_module.repo
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = True
    projects_module.repo = mock_repo

    try:
        # Act
        result = await delete_project(project_id, mock_db)

        # Assert
        assert result is None  # 204 returns None
        mock_repo.delete.assert_called_once_with(mock_db, project_id)
    finally:
        projects_module.repo = original_repo


@pytest.mark.asyncio
async def test_delete_project_not_found_returns_404():
    """Test delete non-existent project returns 404."""
    # Arrange
    mock_db = AsyncMock()
    project_id = uuid4()

    import app.routers.projects as projects_module

    original_repo = projects_module.repo
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = False
    projects_module.repo = mock_repo

    try:
        # Act & Assert
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await delete_project(project_id, mock_db)

        assert exc_info.value.status_code == 404
        assert str(project_id) in exc_info.value.detail
    finally:
        projects_module.repo = original_repo
