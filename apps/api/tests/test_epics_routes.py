"""Integration tests for epic API routes (Story 3.6.1)."""

import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def client():
    """Create async HTTP client for testing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


def create_mock_document(**kwargs):
    """Helper to create mock document object."""
    mock_doc = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_doc, key, value)
    return mock_doc


def create_mock_extracted_epic(**kwargs):
    """Helper to create mock extracted epic object."""
    mock_epic = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_epic, key, value)
    return mock_epic


@pytest.mark.asyncio
async def test_get_epics_with_extracted_data(client):
    """Test GET /api/epics returns documents with extracted_epic data."""
    project_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    # Mock extracted epic with related_stories field
    extracted_epic = create_mock_extracted_epic(
        id=uuid.uuid4(),
        document_id=doc_id,
        status="dev",
        related_stories="story-1-1, story-1-2, story-1-3, story-1-4, story-1-5",
    )

    # Mock document with extracted_epic relationship
    document = create_mock_document(
        id=doc_id,
        project_id=project_id,
        file_path="docs/epics/epic-1-foundation.md",
        content="# Epic 1",
        doc_type="epic",
        title="Foundation & Infrastructure",
        excerpt="Build core foundation...",
        last_modified=datetime.now(timezone.utc),
        extracted_epic=extracted_epic,
    )

    # Patch at the module level where it's used
    with patch("src.routes.epics.EpicRepository") as MockRepo:
        mock_instance = AsyncMock()
        mock_instance.get_by_project = AsyncMock(return_value=[document])
        MockRepo.return_value = mock_instance

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(doc_id)
        assert data[0]["file_path"] == "docs/epics/epic-1-foundation.md"
        assert data[0]["doc_type"] == "epic"
        assert data[0]["extracted_epic"]["status"] == "dev"
        assert data[0]["extracted_epic"]["story_count"] == 5


@pytest.mark.asyncio
async def test_get_epics_without_extracted_data(client):
    """Test GET /api/epics with fallback for documents without extracted_epic."""
    project_id = uuid.uuid4()
    doc_id = uuid.uuid4()

    # Mock document WITHOUT extracted_epic (None)
    document = create_mock_document(
        id=doc_id,
        project_id=project_id,
        file_path="docs/epics/epic-2-new.md",
        content="# Epic 2",
        doc_type="epic",
        title="New Epic",
        excerpt="Not yet extracted...",
        last_modified=datetime.now(timezone.utc),
        extracted_epic=None,  # No extracted data
    )

    with patch("src.routes.epics.EpicRepository") as MockRepo:
        mock_instance = AsyncMock()
        mock_instance.get_by_project = AsyncMock(return_value=[document])
        MockRepo.return_value = mock_instance

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(doc_id)
        # Verify fallback values
        assert data[0]["extracted_epic"]["status"] == "draft"
        assert data[0]["extracted_epic"]["story_count"] == 0


@pytest.mark.asyncio
async def test_get_epics_multiple_with_mixed_data(client):
    """Test GET /api/epics with multiple epics, some with and some without extracted data."""
    project_id = uuid.uuid4()

    # Epic 1: Has extracted data with related_stories
    extracted_1 = create_mock_extracted_epic(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        status="done",
        related_stories="s1, s2, s3, s4, s5, s6, s7, s8",
    )
    doc1 = create_mock_document(
        id=uuid.uuid4(),
        project_id=project_id,
        file_path="docs/epics/epic-1.md",
        content="# Epic 1",
        doc_type="epic",
        title="Epic 1",
        excerpt="",
        last_modified=datetime.now(timezone.utc),
        extracted_epic=extracted_1,
    )

    # Epic 2: No extracted data
    doc2 = create_mock_document(
        id=uuid.uuid4(),
        project_id=project_id,
        file_path="docs/epics/epic-2.md",
        content="# Epic 2",
        doc_type="epic",
        title="Epic 2",
        excerpt="",
        last_modified=datetime.now(timezone.utc),
        extracted_epic=None,
    )

    # Epic 3: Has extracted data with related_stories
    extracted_3 = create_mock_extracted_epic(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        status="dev",
        related_stories="s1, s2, s3",
    )
    doc3 = create_mock_document(
        id=uuid.uuid4(),
        project_id=project_id,
        file_path="docs/epics/epic-3.md",
        content="# Epic 3",
        doc_type="epic",
        title="Epic 3",
        excerpt="",
        last_modified=datetime.now(timezone.utc),
        extracted_epic=extracted_3,
    )

    with patch("src.routes.epics.EpicRepository") as MockRepo:
        mock_instance = AsyncMock()
        mock_instance.get_by_project = AsyncMock(return_value=[doc1, doc2, doc3])
        MockRepo.return_value = mock_instance

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Epic 1: Has extracted data
        assert data[0]["extracted_epic"]["status"] == "done"
        assert data[0]["extracted_epic"]["story_count"] == 8

        # Epic 2: Fallback values
        assert data[1]["extracted_epic"]["status"] == "draft"
        assert data[1]["extracted_epic"]["story_count"] == 0

        # Epic 3: Has extracted data
        assert data[2]["extracted_epic"]["status"] == "dev"
        assert data[2]["extracted_epic"]["story_count"] == 3


@pytest.mark.asyncio
async def test_get_epics_empty_array(client):
    """Test GET /api/epics returns empty array if no epics found."""
    project_id = uuid.uuid4()

    with patch("src.routes.epics.EpicRepository") as MockRepo:
        mock_instance = AsyncMock()
        mock_instance.get_by_project = AsyncMock(return_value=[])
        MockRepo.return_value = mock_instance

        # Execute
        response = await client.get(f"/api/epics?project_id={project_id}")

        # Assert
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
async def test_get_epics_missing_project_id(client):
    """Test GET /api/epics returns 422 if project_id is missing."""
    # Execute without project_id
    response = await client.get("/api/epics")

    # Assert - FastAPI validation error
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("project_id" in str(err).lower() for err in error_detail)
