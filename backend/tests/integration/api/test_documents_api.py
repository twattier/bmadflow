"""Integration tests for Documents API."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_get_document_returns_200_with_content(db_session):
    """Test GET /api/documents/{id} returns 200 with document content."""
    # Arrange - Create test project, project_doc, and document
    from app.models.document import Document
    from app.models.project import Project
    from app.models.project_doc import ProjectDoc

    # Create project
    project = Project(name="Test Project", description="Test")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Create project_doc
    project_doc = ProjectDoc(
        project_id=project.id,
        name="Test Doc",
        github_url="https://github.com/test/repo",
    )
    db_session.add(project_doc)
    await db_session.commit()
    await db_session.refresh(project_doc)

    # Create document
    document = Document(
        project_doc_id=project_doc.id,
        file_path="docs/test.md",
        file_type="md",
        file_size=14,
        content="# Test Content",
    )
    db_session.add(document)
    await db_session.commit()
    await db_session.refresh(document)

    # Act
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/documents/{document.id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(document.id)
    assert data["file_path"] == "docs/test.md"
    assert data["file_type"] == "md"
    assert data["content"] == "# Test Content"
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_document_returns_404_when_not_found(db_session):
    """Test GET /api/documents/{id} returns 404 when document not found."""
    # Arrange
    non_existent_id = uuid4()

    # Act
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/documents/{non_existent_id}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
