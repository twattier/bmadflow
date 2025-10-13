"""Unit tests for GetDocumentTool."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.agents.tools.get_document import GetDocumentTool
from app.models.document import Document
from app.schemas.document import DocumentResponse


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_document():
    """Sample document from database."""
    doc = MagicMock(spec=Document)
    doc.id = uuid4()
    doc.project_doc_id = uuid4()
    doc.file_path = "docs/prd.md"
    doc.file_type = "md"
    doc.file_size = 1024
    doc.content = "# PRD\n\nProject requirements document."
    doc.commit_sha = "abc123"
    doc.created_at = datetime.now()
    doc.updated_at = datetime.now()
    return doc


@pytest.mark.asyncio
async def test_get_document_tool_execute_success(mock_db, sample_document):
    """Test GetDocumentTool.execute() returns DocumentResponse."""
    # Arrange
    tool = GetDocumentTool(document_id=sample_document.id)

    with patch("app.agents.tools.get_document.DocumentRepository") as mock_doc_repo:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = sample_document
        mock_doc_repo.return_value = mock_repo

        # Act
        result = await tool.execute(mock_db)

        # Assert
        assert result is not None
        assert isinstance(result, DocumentResponse)
        assert result.id == sample_document.id
        assert result.file_path == "docs/prd.md"
        assert result.content == "# PRD\n\nProject requirements document."
        assert result.file_size == 1024

        # Verify service calls
        mock_repo.get_by_id.assert_called_once_with(sample_document.id)


@pytest.mark.asyncio
async def test_get_document_tool_document_not_found(mock_db):
    """Test GetDocumentTool.execute() returns None when document not found."""
    # Arrange
    document_id = uuid4()
    tool = GetDocumentTool(document_id=document_id)

    with patch("app.agents.tools.get_document.DocumentRepository") as mock_doc_repo:
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None
        mock_doc_repo.return_value = mock_repo

        # Act
        result = await tool.execute(mock_db)

        # Assert
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(document_id)


def test_get_document_tool_field_validation():
    """Test GetDocumentTool field validation."""
    # Valid tool
    document_id = uuid4()
    tool = GetDocumentTool(document_id=document_id)
    assert tool.document_id == document_id

    # Invalid UUID type
    with pytest.raises(ValueError):
        GetDocumentTool(document_id="not-a-uuid")
