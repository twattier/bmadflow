"""Tests for DocumentRepository."""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from src.repositories.document_repository import DocumentRepository
from src.models.document import Document


@pytest.fixture
def mock_db():
    """Mock async database session."""
    db = AsyncMock()
    return db


@pytest.fixture
def document_repo(mock_db):
    """Create DocumentRepository with mocked database."""
    return DocumentRepository(mock_db)


@pytest.mark.asyncio
async def test_get_by_project_id(document_repo, mock_db):
    """Test getting documents by project ID."""
    project_id = uuid.uuid4()
    documents = [
        Document(
            id=uuid.uuid4(),
            project_id=project_id,
            file_path="docs/prd/overview.md",
            content="# Overview",
            doc_type="scoping",
            title="Overview",
            excerpt="# Overview",
            created_at=datetime.utcnow(),
        ),
        Document(
            id=uuid.uuid4(),
            project_id=project_id,
            file_path="docs/architecture/tech-stack.md",
            content="# Tech Stack",
            doc_type="architecture",
            title="Tech Stack",
            excerpt="# Tech Stack",
            created_at=datetime.utcnow(),
        ),
    ]

    # Mock database result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = documents
    mock_db.execute.return_value = mock_result

    # Execute
    result = await document_repo.get_by_project_id(project_id)

    # Assert
    assert len(result) == 2
    assert result[0].file_path == "docs/prd/overview.md"
    assert result[1].file_path == "docs/architecture/tech-stack.md"
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_project_id_empty(document_repo, mock_db):
    """Test getting documents by project ID when none exist."""
    project_id = uuid.uuid4()

    # Mock database result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    # Execute
    result = await document_repo.get_by_project_id(project_id)

    # Assert
    assert len(result) == 0


@pytest.mark.asyncio
async def test_upsert_new_document(document_repo, mock_db):
    """Test upserting a new document (insert)."""
    project_id = uuid.uuid4()
    document_data = {
        "project_id": project_id,
        "file_path": "docs/prd/overview.md",
        "content": "# Overview\nContent here",
        "doc_type": "scoping",
        "title": "Overview",
        "excerpt": "# Overview",
        "last_modified": datetime.utcnow(),
    }

    # Mock the created document
    created_document = Document(id=uuid.uuid4(), **document_data)

    # Mock database operations
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = created_document
    mock_db.execute.return_value = mock_result
    mock_db.commit = AsyncMock()

    # Execute
    result = await document_repo.upsert(**document_data)

    # Assert
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
    assert result == created_document


@pytest.mark.asyncio
async def test_upsert_existing_document(document_repo, mock_db):
    """Test upserting an existing document (update)."""
    project_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_data = {
        "project_id": project_id,
        "file_path": "docs/prd/overview.md",
        "content": "# Overview\nUpdated content",
        "doc_type": "scoping",
        "title": "Overview Updated",
        "excerpt": "# Overview",
        "last_modified": datetime.utcnow(),
    }

    # Mock the updated document
    updated_document = Document(id=document_id, **document_data)

    # Mock database operations
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = updated_document
    mock_db.execute.return_value = mock_result
    mock_db.commit = AsyncMock()

    # Execute
    result = await document_repo.upsert(**document_data)

    # Assert
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
    assert result.content == "# Overview\nUpdated content"
    assert result.title == "Overview Updated"
