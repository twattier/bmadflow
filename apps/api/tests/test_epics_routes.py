"""Integration tests for epic API routes (Story 3.0 - AC3)."""

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


def create_mock_epic(**kwargs):
    """Helper to create mock epic object with document relationship."""
    mock_epic = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_epic, key, value)
    return mock_epic


def create_mock_document(**kwargs):
    """Helper to create mock document object."""
    mock_doc = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_doc, key, value)
    return mock_doc


@pytest.mark.asyncio
async def test_get_epics_by_project(client):
    """Test AC3: Get all epics for a project with extracted metadata."""
    project_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    with patch("src.repositories.epic_repository.EpicRepository") as mock_epic_repo_class:
        mock_epic_repo = AsyncMock()

        # Mock document
        document = create_mock_document(
            id=doc_id,
            project_id=project_id,
            file_path="docs/epics/epic-1.md",
            last_modified=datetime.now(timezone.utc),
        )

        # Mock epic with document relationship
        epic = create_mock_epic(
            id=uuid.uuid4(),
            document_id=doc_id,
            epic_number=1,
            title="Foundation, GitHub Integration & Dashboard Shell",
            goal="Establish core infrastructure...",
            status="done",
            story_count=8,
            confidence_score=0.95,
            extracted_at=datetime.now(timezone.utc),
        )
        epic.document = document  # Set relationship

        mock_epic_repo.get_by_project.return_value = [epic]
        mock_epic_repo_class.return_value = mock_epic_repo

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["epic_number"] == 1
        assert data[0]["title"] == "Foundation, GitHub Integration & Dashboard Shell"
        assert data[0]["goal"] == "Establish core infrastructure..."
        assert data[0]["status"] == "done"
        assert data[0]["story_count"] == 8
        assert data[0]["confidence_score"] == 0.95
        assert data[0]["document"]["file_path"] == "docs/epics/epic-1.md"

        # Verify repository called with correct params
        mock_epic_repo.get_by_project.assert_called_once_with(project_id)


@pytest.mark.asyncio
async def test_get_epics_sorted_by_epic_number(client):
    """Test AC3: Epics are sorted by epic_number (ascending)."""
    project_id = uuid.uuid4()

    with patch("src.repositories.epic_repository.EpicRepository") as mock_epic_repo_class:
        mock_epic_repo = AsyncMock()

        # Create multiple epics with different numbers
        epics = []
        for num in [1, 2, 3]:  # Already sorted (repository does sorting)
            doc = create_mock_document(
                id=uuid.uuid4(),
                project_id=project_id,
                file_path=f"docs/epics/epic-{num}.md",
                last_modified=datetime.now(timezone.utc),
            )

            epic = create_mock_epic(
                id=uuid.uuid4(),
                document_id=doc.id,
                epic_number=num,
                title=f"Epic {num} Title",
                goal=f"Epic {num} goal...",
                status="draft",
                story_count=5,
                confidence_score=0.9,
                extracted_at=datetime.now(timezone.utc),
            )
            epic.document = doc
            epics.append(epic)

        mock_epic_repo.get_by_project.return_value = epics
        mock_epic_repo_class.return_value = mock_epic_repo

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Verify sorted order
        assert data[0]["epic_number"] == 1
        assert data[1]["epic_number"] == 2
        assert data[2]["epic_number"] == 3


@pytest.mark.asyncio
async def test_get_epics_empty_array(client):
    """Test AC3: Return empty array if no epics found."""
    project_id = uuid.uuid4()

    with patch("src.repositories.epic_repository.EpicRepository") as mock_epic_repo_class:
        mock_epic_repo = AsyncMock()
        mock_epic_repo.get_by_project.return_value = []
        mock_epic_repo_class.return_value = mock_epic_repo

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_get_epics_missing_project_id(client):
    """Test AC3: Return 422 if project_id query parameter is missing."""
    # Execute without project_id
    response = await client.get("/api/epics")

    # Assert - FastAPI validation error
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("project_id" in str(err).lower() for err in error_detail)


@pytest.mark.asyncio
async def test_get_epics_includes_document_metadata(client):
    """Test AC3: Response includes document title, file_path, last_modified."""
    project_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    last_modified = datetime(2025, 10, 1, 14, 32, 15, tzinfo=timezone.utc)

    with patch("src.repositories.epic_repository.EpicRepository") as mock_epic_repo_class:
        mock_epic_repo = AsyncMock()

        # Mock document with specific metadata
        document = create_mock_document(
            id=doc_id,
            project_id=project_id,
            file_path="docs/epics/epic-2.md",
            last_modified=last_modified,
        )

        epic = create_mock_epic(
            id=uuid.uuid4(),
            document_id=doc_id,
            epic_number=2,
            title="AI-Powered Extraction Engine",
            goal="Build OLLAMA-based extraction...",
            status="in_progress",
            story_count=12,
            confidence_score=0.97,
            extracted_at=datetime.now(timezone.utc),
        )
        epic.document = document

        mock_epic_repo.get_by_project.return_value = [epic]
        mock_epic_repo_class.return_value = mock_epic_repo

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Verify document metadata is included
        doc_data = data[0]["document"]
        assert doc_data["file_path"] == "docs/epics/epic-2.md"
        assert doc_data["last_modified"] == last_modified.isoformat().replace(
            "+00:00", "Z"
        )


@pytest.mark.asyncio
async def test_get_epics_with_null_optional_fields(client):
    """Test AC3: Handle epics with null optional fields (epic_number, goal, confidence_score)."""
    project_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    with patch("src.repositories.epic_repository.EpicRepository") as mock_epic_repo_class:
        mock_epic_repo = AsyncMock()

        document = create_mock_document(
            id=doc_id,
            project_id=project_id,
            file_path="docs/epics/epic-draft.md",
            last_modified=datetime.now(timezone.utc),
        )

        # Epic with null optional fields
        epic = create_mock_epic(
            id=uuid.uuid4(),
            document_id=doc_id,
            epic_number=None,  # Optional
            title="Draft Epic (No Number)",
            goal=None,  # Optional
            status="draft",
            story_count=0,
            confidence_score=None,  # Optional
            extracted_at=datetime.now(timezone.utc),
        )
        epic.document = document

        mock_epic_repo.get_by_project.return_value = [epic]
        mock_epic_repo_class.return_value = mock_epic_repo

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["epic_number"] is None
        assert data[0]["goal"] is None
        assert data[0]["confidence_score"] is None
        assert data[0]["title"] == "Draft Epic (No Number)"
