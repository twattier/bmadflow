"""Unit tests for ProjectDoc API endpoints."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.routers import project_docs
from app.schemas.project_doc import ProjectDocCreate, ProjectDocResponse, ProjectDocUpdate


class TestCreateProjectDoc:
    """Tests for create_project_doc endpoint."""

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_create_project_doc_success(self, mock_repo_class):
        """Test creating ProjectDoc with valid data succeeds."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_id = uuid4()
        project_doc_id = uuid4()
        data = ProjectDocCreate(
            name="Test Docs",
            description="Test",
            github_url="https://github.com/user/repo",
            github_folder_path="docs",
        )
        expected_project_doc = ProjectDocResponse(
            id=project_doc_id,
            project_id=project_id,
            name="Test Docs",
            description="Test",
            github_url="https://github.com/user/repo",
            github_folder_path="docs",
            last_synced_at=None,
            last_github_commit_date=None,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        mock_repo.create.return_value = expected_project_doc

        # Act
        result = await project_docs.create_project_doc(project_id, data, mock_db)

        # Assert
        assert result.name == "Test Docs"
        assert result.github_url == "https://github.com/user/repo"
        mock_repo.create.assert_called_once_with(mock_db, project_id, data)

    def test_create_project_doc_missing_name(self):
        """Test creating ProjectDoc without name returns validation error."""
        with pytest.raises(ValueError):
            ProjectDocCreate(github_url="https://github.com/user/repo", github_folder_path="docs")

    def test_create_project_doc_invalid_github_url(self):
        """Test creating ProjectDoc with non-GitHub URL returns validation error."""
        with pytest.raises(ValueError, match="Must be a GitHub repository URL"):
            ProjectDocCreate(
                name="Test Docs",
                github_url="https://gitlab.com/user/repo",
                github_folder_path="docs",
            )


class TestListProjectDocs:
    """Tests for list_project_docs endpoint."""

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_list_project_docs_returns_all(self, mock_repo_class):
        """Test list ProjectDocs returns all ProjectDocs for a project."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_id = uuid4()
        expected_docs = [
            ProjectDocResponse(
                id=uuid4(),
                project_id=project_id,
                name="Doc 1",
                description=None,
                github_url="https://github.com/user/repo1",
                github_folder_path=None,
                last_synced_at=None,
                last_github_commit_date=None,
                created_at="2025-01-02T00:00:00",
                updated_at="2025-01-02T00:00:00",
            ),
            ProjectDocResponse(
                id=uuid4(),
                project_id=project_id,
                name="Doc 2",
                description=None,
                github_url="https://github.com/user/repo2",
                github_folder_path="docs",
                last_synced_at=None,
                last_github_commit_date=None,
                created_at="2025-01-01T00:00:00",
                updated_at="2025-01-01T00:00:00",
            ),
        ]
        mock_repo.get_all_by_project.return_value = expected_docs

        # Act
        result = await project_docs.list_project_docs(project_id, mock_db)

        # Assert
        assert len(result) == 2
        assert result[0].name == "Doc 1"
        assert result[1].name == "Doc 2"
        mock_repo.get_all_by_project.assert_called_once_with(mock_db, project_id)


class TestGetProjectDoc:
    """Tests for get_project_doc endpoint."""

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_get_project_doc_returns_correct_doc(self, mock_repo_class):
        """Test get ProjectDoc by ID returns correct ProjectDoc."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_doc_id = uuid4()
        expected_doc = ProjectDocResponse(
            id=project_doc_id,
            project_id=uuid4(),
            name="Test Doc",
            description="Test",
            github_url="https://github.com/user/repo",
            github_folder_path="docs",
            last_synced_at=None,
            last_github_commit_date=None,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        mock_repo.get_by_id.return_value = expected_doc

        # Act
        result = await project_docs.get_project_doc(project_doc_id, mock_db)

        # Assert
        assert result.id == project_doc_id
        assert result.name == "Test Doc"
        mock_repo.get_by_id.assert_called_once_with(mock_db, project_doc_id)

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_get_project_doc_not_found_returns_404(self, mock_repo_class):
        """Test get ProjectDoc with invalid ID returns 404."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_doc_id = uuid4()
        mock_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_docs.get_project_doc(project_doc_id, mock_db)

        assert exc_info.value.status_code == 404
        assert f"ProjectDoc {project_doc_id} not found" in str(exc_info.value.detail)


class TestUpdateProjectDoc:
    """Tests for update_project_doc endpoint."""

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_update_project_doc_modifies_fields(self, mock_repo_class):
        """Test update ProjectDoc modifies fields."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_doc_id = uuid4()
        data = ProjectDocUpdate(name="Updated Name", description="Updated")
        updated_doc = ProjectDocResponse(
            id=project_doc_id,
            project_id=uuid4(),
            name="Updated Name",
            description="Updated",
            github_url="https://github.com/user/repo",
            github_folder_path="docs",
            last_synced_at=None,
            last_github_commit_date=None,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-02T00:00:00",
        )
        mock_repo.update.return_value = updated_doc

        # Act
        result = await project_docs.update_project_doc(project_doc_id, data, mock_db)

        # Assert
        assert result.name == "Updated Name"
        assert result.description == "Updated"
        mock_repo.update.assert_called_once_with(mock_db, project_doc_id, data)

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_update_project_doc_not_found_returns_404(self, mock_repo_class):
        """Test update ProjectDoc with invalid ID returns 404."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_doc_id = uuid4()
        data = ProjectDocUpdate(name="Updated Name")
        mock_repo.update.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_docs.update_project_doc(project_doc_id, data, mock_db)

        assert exc_info.value.status_code == 404


class TestDeleteProjectDoc:
    """Tests for delete_project_doc endpoint."""

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_delete_project_doc_returns_204(self, mock_repo_class):
        """Test delete ProjectDoc returns 204."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_doc_id = uuid4()
        mock_repo.delete.return_value = True

        # Act
        result = await project_docs.delete_project_doc(project_doc_id, mock_db)

        # Assert
        assert result is None
        mock_repo.delete.assert_called_once_with(mock_db, project_doc_id)

    @pytest.mark.asyncio
    @patch.object(project_docs, "ProjectDocRepository")
    async def test_delete_project_doc_not_found_returns_404(self, mock_repo_class):
        """Test delete ProjectDoc with invalid ID returns 404."""
        # Arrange
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        project_doc_id = uuid4()
        mock_repo.delete.return_value = False

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await project_docs.delete_project_doc(project_doc_id, mock_db)

        assert exc_info.value.status_code == 404
