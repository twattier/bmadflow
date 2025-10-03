"""Integration tests for document API routes (Story 3.0 - AC1, AC2, AC5)."""

import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
def client():
    """Create async HTTP client for testing."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def create_mock_document(**kwargs):
    """Helper to create mock document object."""
    mock_doc = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_doc, key, value)
    return mock_doc


def create_mock_project(**kwargs):
    """Helper to create mock project object."""
    mock_proj = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_proj, key, value)
    return mock_proj


@pytest.mark.asyncio
async def test_get_documents_by_type_epic(client):
    """Test AC1: Filter documents by type='epic'."""
    project_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
            # Mock project exists
            mock_project_repo = AsyncMock()
            mock_project = create_mock_project(
                id=project_id,
                name="test-repo",
                github_url="https://github.com/owner/test-repo",
                sync_status="idle",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_project_repo.get_by_id.return_value = mock_project
            mock_project_repo_class.return_value = mock_project_repo

            # Mock documents filtered by type
            mock_doc_repo = AsyncMock()
            epic_doc = create_mock_document(
                id=uuid.uuid4(),
                project_id=project_id,
                file_path="docs/epics/epic-1.md",
                content="# Epic 1",
                doc_type="epic",
                title="Epic 1: Foundation",
                excerpt="Epic 1 description...",
                last_modified=datetime.now(timezone.utc),
                extraction_status="completed",
                extraction_confidence=0.95,
                created_at=datetime.now(timezone.utc),
            )
            mock_doc_repo.get_by_type.return_value = [epic_doc]
            mock_doc_repo_class.return_value = mock_doc_repo

            # Execute
            response = await client.get(
                f"/api/projects/{project_id}/documents?type=epic"
            )

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["doc_type"] == "epic"
            assert data[0]["file_path"] == "docs/epics/epic-1.md"
            assert data[0]["title"] == "Epic 1: Foundation"

            # Verify repository called with correct params
            mock_doc_repo.get_by_type.assert_called_once_with(project_id, "epic")


@pytest.mark.asyncio
async def test_get_documents_all_types(client):
    """Test AC1: Get all documents when type filter is omitted."""
    project_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
            # Mock project exists
            mock_project_repo = AsyncMock()
            mock_project = create_mock_project(
                id=project_id,
                name="test-repo",
                github_url="https://github.com/owner/test-repo",
                sync_status="idle",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_project_repo.get_by_id.return_value = mock_project
            mock_project_repo_class.return_value = mock_project_repo

            # Mock all documents
            mock_doc_repo = AsyncMock()
            docs = [
                create_mock_document(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    file_path=f"docs/{dtype}/doc.md",
                    content="# Doc",
                    doc_type=dtype,
                    title=f"{dtype.capitalize()} Doc",
                    excerpt="Description...",
                    last_modified=datetime.now(timezone.utc),
                    extraction_status="completed",
                    extraction_confidence=0.9,
                    created_at=datetime.now(timezone.utc),
                )
                for dtype in ["scoping", "architecture", "epic", "story"]
            ]
            mock_doc_repo.get_by_type.return_value = docs
            mock_doc_repo_class.return_value = mock_doc_repo

            # Execute
            response = await client.get(f"/api/projects/{project_id}/documents")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 4

            # Verify repository called with None for type
            mock_doc_repo.get_by_type.assert_called_once_with(project_id, None)


@pytest.mark.asyncio
async def test_get_documents_project_not_found(client):
    """Test AC1: Return 404 if project not found."""
    project_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        mock_project_repo = AsyncMock()
        mock_project_repo.get_by_id.return_value = None  # Project not found
        mock_project_repo_class.return_value = mock_project_repo

        # Execute
        response = await client.get(f"/api/projects/{project_id}/documents")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_documents_empty_array(client):
    """Test AC1: Return empty array if no documents match filter."""
    project_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
            # Mock project exists
            mock_project_repo = AsyncMock()
            mock_project = create_mock_project(
                id=project_id,
                name="test-repo",
                github_url="https://github.com/owner/test-repo",
                sync_status="idle",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            mock_project_repo.get_by_id.return_value = mock_project
            mock_project_repo_class.return_value = mock_project_repo

            # Mock no documents
            mock_doc_repo = AsyncMock()
            mock_doc_repo.get_by_type.return_value = []
            mock_doc_repo_class.return_value = mock_doc_repo

            # Execute
            response = await client.get(
                f"/api/projects/{project_id}/documents?type=qa"
            )

            # Assert
            assert response.status_code == 200
            assert response.json() == []


@pytest.mark.asyncio
async def test_get_document_by_id_success(client):
    """Test AC2: Get single document with full content."""
    doc_id = uuid.uuid4()
    project_id = uuid.uuid4()

    with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
        mock_doc_repo = AsyncMock()
        full_content = "# Epic 3: Multi-View Dashboard\n\n**Status:** Draft\n\nFull content here..."
        document = create_mock_document(
            id=doc_id,
            project_id=project_id,
            file_path="docs/epics/epic-3.md",
            content=full_content,
            doc_type="epic",
            title="Epic 3: Multi-View Dashboard",
            excerpt="Create 4-view dashboard...",
            last_modified=datetime.now(timezone.utc),
            extraction_status="completed",
            extraction_confidence=0.92,
            created_at=datetime.now(timezone.utc),
        )
        mock_doc_repo.get_by_id.return_value = document
        mock_doc_repo_class.return_value = mock_doc_repo

        # Execute
        response = await client.get(f"/api/documents/{doc_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(doc_id)
        assert data["content"] == full_content
        assert data["title"] == "Epic 3: Multi-View Dashboard"
        assert "excerpt" in data


@pytest.mark.asyncio
async def test_get_document_by_id_not_found(client):
    """Test AC2: Return 404 if document not found."""
    doc_id = uuid.uuid4()

    with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
        mock_doc_repo = AsyncMock()
        mock_doc_repo.get_by_id.return_value = None
        mock_doc_repo_class.return_value = mock_doc_repo

        # Execute
        response = await client.get(f"/api/documents/{doc_id}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_resolve_document_path_relative(client):
    """Test AC5: Resolve relative path (../epic-1.md)."""
    project_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
        mock_doc_repo = AsyncMock()
        document = create_mock_document(
            id=doc_id,
            project_id=project_id,
            file_path="docs/epics/epic-1.md",
            content="# Epic 1",
            doc_type="epic",
            title="Epic 1: Foundation",
            excerpt="Foundation epic...",
            last_modified=datetime.now(timezone.utc),
            extraction_status="completed",
            extraction_confidence=0.95,
            created_at=datetime.now(timezone.utc),
        )
        mock_doc_repo.resolve_path.return_value = document
        mock_doc_repo_class.return_value = mock_doc_repo

        # Execute
        response = await client.get(
            f"/api/documents/resolve?file_path=../epic-1.md&project_id={project_id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(doc_id)
        assert data["file_path"] == "docs/epics/epic-1.md"
        assert data["title"] == "Epic 1: Foundation"
        assert data["doc_type"] == "epic"

        # Verify repository was called with correct params
        mock_doc_repo.resolve_path.assert_called_once_with(project_id, "../epic-1.md")


@pytest.mark.asyncio
async def test_resolve_document_path_absolute(client):
    """Test AC5: Resolve absolute path (/docs/architecture.md)."""
    project_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
        mock_doc_repo = AsyncMock()
        document = create_mock_document(
            id=doc_id,
            project_id=project_id,
            file_path="docs/architecture.md",
            content="# Architecture",
            doc_type="architecture",
            title="BMADFlow Architecture",
            excerpt="System architecture...",
            last_modified=datetime.now(timezone.utc),
            extraction_status="completed",
            extraction_confidence=0.98,
            created_at=datetime.now(timezone.utc),
        )
        mock_doc_repo.resolve_path.return_value = document
        mock_doc_repo_class.return_value = mock_doc_repo

        # Execute
        response = await client.get(
            f"/api/documents/resolve?file_path=/docs/architecture.md&project_id={project_id}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["file_path"] == "docs/architecture.md"


@pytest.mark.asyncio
async def test_resolve_document_path_not_found(client):
    """Test AC5: Return 404 if document path not found (broken link detection)."""
    project_id = uuid.uuid4()

    with patch("src.repositories.document_repository.DocumentRepository") as mock_doc_repo_class:
        mock_doc_repo = AsyncMock()
        mock_doc_repo.resolve_path.return_value = None
        mock_doc_repo_class.return_value = mock_doc_repo

        # Execute
        response = await client.get(
            f"/api/documents/resolve?file_path=../missing.md&project_id={project_id}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_resolve_document_path_missing_params(client):
    """Test AC5: Return 422 if required query params missing."""
    # Missing project_id
    response = await client.get("/api/documents/resolve?file_path=../epic-1.md")
    assert response.status_code == 422

    # Missing file_path
    project_id = uuid.uuid4()
    response = await client.get(f"/api/documents/resolve?project_id={project_id}")
    assert response.status_code == 422
