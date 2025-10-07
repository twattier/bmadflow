"""Unit tests for DocumentService."""

import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from app.models.document import Document
from app.services.document_service import DocumentService


@pytest.fixture
def mock_document_repo():
    """Mock document repository."""
    return Mock()


@pytest.fixture
def document_service(mock_document_repo):
    """DocumentService with mocked repository."""
    return DocumentService(mock_document_repo)


def create_mock_document(file_path: str, file_type: str = "md", file_size: int = 1000):
    """Helper to create mock document."""
    doc = Mock(spec=Document)
    doc.id = uuid.uuid4()
    doc.project_doc_id = uuid.uuid4()
    doc.file_path = file_path
    doc.file_type = file_type
    doc.file_size = file_size
    return doc


@pytest.mark.asyncio
async def test_build_file_tree_empty_project(document_service, mock_document_repo):
    """Test file tree with no documents."""
    # Arrange
    project_id = uuid.uuid4()
    mock_document_repo.list_by_project_id = AsyncMock(return_value=[])

    # Act
    result = await document_service.build_file_tree(project_id)

    # Assert
    assert result.project_id == project_id
    assert result.tree == []
    mock_document_repo.list_by_project_id.assert_called_once_with(project_id)


@pytest.mark.asyncio
async def test_build_file_tree_single_level_files(document_service, mock_document_repo):
    """Test file tree with root-level files only."""
    # Arrange
    project_id = uuid.uuid4()
    mock_documents = [
        create_mock_document("README.md"),
        create_mock_document("LICENSE", file_type="txt"),
    ]
    mock_document_repo.list_by_project_id = AsyncMock(return_value=mock_documents)

    # Act
    result = await document_service.build_file_tree(project_id)

    # Assert
    assert result.project_id == project_id
    assert len(result.tree) == 2
    # Check alphabetical sorting
    assert result.tree[0].name == "LICENSE"
    assert result.tree[1].name == "README.md"
    # Check file properties
    assert result.tree[0].type == "file"
    assert result.tree[0].path == "LICENSE"
    assert result.tree[0].id == mock_documents[1].id


@pytest.mark.asyncio
async def test_build_file_tree_nested_folders(document_service, mock_document_repo):
    """Test file tree with nested folder structure."""
    # Arrange
    project_id = uuid.uuid4()
    mock_documents = [
        create_mock_document("docs/architecture.md"),
        create_mock_document("docs/prd.md"),
        create_mock_document("docs/architecture/backend.md"),
        create_mock_document("README.md"),
    ]
    mock_document_repo.list_by_project_id = AsyncMock(return_value=mock_documents)

    # Act
    result = await document_service.build_file_tree(project_id)

    # Assert
    assert result.project_id == project_id
    assert len(result.tree) == 2  # "docs" folder + "README.md" file

    # Check sorting: folders first
    assert result.tree[0].type == "folder"
    assert result.tree[0].name == "docs"
    assert result.tree[1].type == "file"
    assert result.tree[1].name == "README.md"

    # Check nested "docs" folder
    docs_folder = result.tree[0]
    assert docs_folder.path == "docs"
    assert len(docs_folder.children) == 3  # "architecture" folder + 2 files

    # Verify nested structure
    arch_folder = docs_folder.children[0]
    assert arch_folder.type == "folder"
    assert arch_folder.name == "architecture"
    assert len(arch_folder.children) == 1
    assert arch_folder.children[0].name == "backend.md"


@pytest.mark.asyncio
async def test_build_file_tree_sorting(document_service, mock_document_repo):
    """Test that folders come before files and both are alphabetically sorted."""
    # Arrange
    project_id = uuid.uuid4()
    mock_documents = [
        create_mock_document("zebra.md"),
        create_mock_document("apple/file.md"),
        create_mock_document("banana/file.md"),
        create_mock_document("aardvark.md"),
    ]
    mock_document_repo.list_by_project_id = AsyncMock(return_value=mock_documents)

    # Act
    result = await document_service.build_file_tree(project_id)

    # Assert
    assert len(result.tree) == 4
    # Folders first (alphabetical)
    assert result.tree[0].type == "folder"
    assert result.tree[0].name == "apple"
    assert result.tree[1].type == "folder"
    assert result.tree[1].name == "banana"
    # Then files (alphabetical)
    assert result.tree[2].type == "file"
    assert result.tree[2].name == "aardvark.md"
    assert result.tree[3].type == "file"
    assert result.tree[3].name == "zebra.md"


@pytest.mark.asyncio
async def test_build_file_tree_deep_nesting(document_service, mock_document_repo):
    """Test file tree with 3-level deep nesting."""
    # Arrange
    project_id = uuid.uuid4()
    mock_documents = [
        create_mock_document("docs/architecture/backend/api.md"),
        create_mock_document("docs/architecture/backend/services.md"),
        create_mock_document("docs/architecture/frontend.md"),
    ]
    mock_document_repo.list_by_project_id = AsyncMock(return_value=mock_documents)

    # Act
    result = await document_service.build_file_tree(project_id)

    # Assert
    # Navigate to deeply nested file
    docs = result.tree[0]
    assert docs.name == "docs"
    arch = docs.children[0]
    assert arch.name == "architecture"
    assert len(arch.children) == 2  # "backend" folder + "frontend.md" file

    backend = arch.children[0]
    assert backend.type == "folder"
    assert backend.name == "backend"
    assert len(backend.children) == 2
    assert backend.children[0].name == "api.md"
    assert backend.children[1].name == "services.md"
