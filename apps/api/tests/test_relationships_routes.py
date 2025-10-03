"""Integration tests for relationship API routes (Story 3.0 - AC4)."""

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


def create_mock_project(**kwargs):
    """Helper to create mock project object."""
    mock_proj = MagicMock()
    for key, value in kwargs.items():
        setattr(mock_proj, key, value)
    return mock_proj


@pytest.mark.asyncio
async def test_get_relationships_all_epics(client):
    """Test AC4: Get all epics + stories when epic_id is omitted."""
    project_id = uuid.uuid4()
    epic1_id = uuid.uuid4()
    epic2_id = uuid.uuid4()
    story1_id = uuid.uuid4()
    story2_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch(
            "src.repositories.relationship_repository.RelationshipRepository"
        ) as mock_rel_repo_class:
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

            # Mock graph data
            mock_rel_repo = AsyncMock()
            graph_data = {
                "nodes": [
                    {
                        "id": str(epic1_id),
                        "title": "Epic 1: Foundation",
                        "type": "epic",
                        "status": "done",
                        "document_id": str(uuid.uuid4()),
                    },
                    {
                        "id": str(epic2_id),
                        "title": "Epic 2: Extraction",
                        "type": "epic",
                        "status": "in_progress",
                        "document_id": str(uuid.uuid4()),
                    },
                    {
                        "id": str(story1_id),
                        "title": "Story 1.1: Project Setup",
                        "type": "story",
                        "status": "done",
                        "document_id": str(uuid.uuid4()),
                    },
                    {
                        "id": str(story2_id),
                        "title": "Story 2.1: Epic Detection",
                        "type": "story",
                        "status": "done",
                        "document_id": str(uuid.uuid4()),
                    },
                ],
                "edges": [
                    {
                        "source_id": str(epic1_id),
                        "target_id": str(story1_id),
                        "type": "contains",
                    },
                    {
                        "source_id": str(epic2_id),
                        "target_id": str(story2_id),
                        "type": "contains",
                    },
                ],
            }
            mock_rel_repo.get_graph_data.return_value = graph_data
            mock_rel_repo_class.return_value = mock_rel_repo

            # Execute
            response = await client.get(f"/api/projects/{project_id}/relationships")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["nodes"]) == 4
            assert len(data["edges"]) == 2

            # Verify epic nodes
            epic_nodes = [n for n in data["nodes"] if n["type"] == "epic"]
            assert len(epic_nodes) == 2

            # Verify story nodes
            story_nodes = [n for n in data["nodes"] if n["type"] == "story"]
            assert len(story_nodes) == 2

            # Verify repository called with correct params
            mock_rel_repo.get_graph_data.assert_called_once_with(project_id, None)


@pytest.mark.asyncio
async def test_get_relationships_filtered_by_epic(client):
    """Test AC4: Get only specific epic and its stories when epic_id provided."""
    project_id = uuid.uuid4()
    epic_id = uuid.uuid4()
    story1_id = uuid.uuid4()
    story2_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch(
            "src.repositories.relationship_repository.RelationshipRepository"
        ) as mock_rel_repo_class:
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

            # Mock graph data for single epic
            mock_rel_repo = AsyncMock()
            graph_data = {
                "nodes": [
                    {
                        "id": str(epic_id),
                        "title": "Epic 1: Foundation",
                        "type": "epic",
                        "status": "done",
                        "document_id": str(uuid.uuid4()),
                    },
                    {
                        "id": str(story1_id),
                        "title": "Story 1.1: Project Setup",
                        "type": "story",
                        "status": "done",
                        "document_id": str(uuid.uuid4()),
                    },
                    {
                        "id": str(story2_id),
                        "title": "Story 1.2: Database Schema",
                        "type": "story",
                        "status": "done",
                        "document_id": str(uuid.uuid4()),
                    },
                ],
                "edges": [
                    {
                        "source_id": str(epic_id),
                        "target_id": str(story1_id),
                        "type": "contains",
                    },
                    {
                        "source_id": str(epic_id),
                        "target_id": str(story2_id),
                        "type": "contains",
                    },
                ],
            }
            mock_rel_repo.get_graph_data.return_value = graph_data
            mock_rel_repo_class.return_value = mock_rel_repo

            # Execute
            response = await client.get(
                f"/api/projects/{project_id}/relationships?epic_id={epic_id}"
            )

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["nodes"]) == 3  # 1 epic + 2 stories
            assert len(data["edges"]) == 2

            # Verify only one epic node
            epic_nodes = [n for n in data["nodes"] if n["type"] == "epic"]
            assert len(epic_nodes) == 1
            assert epic_nodes[0]["id"] == str(epic_id)

            # Verify repository called with epic_id filter
            mock_rel_repo.get_graph_data.assert_called_once_with(project_id, epic_id)


@pytest.mark.asyncio
async def test_get_relationships_project_not_found(client):
    """Test AC4: Return 404 if project not found."""
    project_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        mock_project_repo = AsyncMock()
        mock_project_repo.get_by_id.return_value = None
        mock_project_repo_class.return_value = mock_project_repo

        # Execute
        response = await client.get(f"/api/projects/{project_id}/relationships")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_relationships_epic_not_found(client):
    """Test AC4: Return 404 if epic_id specified but not found."""
    project_id = uuid.uuid4()
    epic_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch(
            "src.repositories.relationship_repository.RelationshipRepository"
        ) as mock_rel_repo_class:
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

            # Mock empty graph data (epic not found)
            mock_rel_repo = AsyncMock()
            mock_rel_repo.get_graph_data.return_value = {"nodes": [], "edges": []}
            mock_rel_repo_class.return_value = mock_rel_repo

            # Execute
            response = await client.get(
                f"/api/projects/{project_id}/relationships?epic_id={epic_id}"
            )

            # Assert
            assert response.status_code == 404
            assert "epic" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_relationships_empty_graph(client):
    """Test AC4: Return empty nodes/edges when no epics exist (but project exists)."""
    project_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch(
            "src.repositories.relationship_repository.RelationshipRepository"
        ) as mock_rel_repo_class:
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

            # Mock empty graph data
            mock_rel_repo = AsyncMock()
            mock_rel_repo.get_graph_data.return_value = {"nodes": [], "edges": []}
            mock_rel_repo_class.return_value = mock_rel_repo

            # Execute (no epic_id filter)
            response = await client.get(f"/api/projects/{project_id}/relationships")

            # Assert - Should return 200 with empty arrays
            assert response.status_code == 200
            data = response.json()
            assert data["nodes"] == []
            assert data["edges"] == []


@pytest.mark.asyncio
async def test_get_relationships_graph_structure(client):
    """Test AC4: Verify correct GraphData structure with nodes and edges."""
    project_id = uuid.uuid4()
    epic_id = uuid.uuid4()
    story_id = uuid.uuid4()
    epic_doc_id = uuid.uuid4()
    story_doc_id = uuid.uuid4()

    with patch("src.repositories.project_repository.ProjectRepository") as mock_project_repo_class:
        with patch(
            "src.repositories.relationship_repository.RelationshipRepository"
        ) as mock_rel_repo_class:
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

            # Mock graph data with specific structure
            mock_rel_repo = AsyncMock()
            graph_data = {
                "nodes": [
                    {
                        "id": str(epic_id),
                        "title": "Epic 3: Multi-View Dashboard",
                        "type": "epic",
                        "status": "draft",
                        "document_id": str(epic_doc_id),
                    },
                    {
                        "id": str(story_id),
                        "title": "Story 3.0: Backend API Endpoints",
                        "type": "story",
                        "status": "ready",
                        "document_id": str(story_doc_id),
                    },
                ],
                "edges": [
                    {
                        "source_id": str(epic_id),
                        "target_id": str(story_id),
                        "type": "contains",
                    }
                ],
            }
            mock_rel_repo.get_graph_data.return_value = graph_data
            mock_rel_repo_class.return_value = mock_rel_repo

            # Execute
            response = await client.get(f"/api/projects/{project_id}/relationships")

            # Assert
            assert response.status_code == 200
            data = response.json()

            # Verify nodes structure
            assert "nodes" in data
            assert len(data["nodes"]) == 2
            epic_node = data["nodes"][0]
            assert epic_node["id"] == str(epic_id)
            assert epic_node["title"] == "Epic 3: Multi-View Dashboard"
            assert epic_node["type"] == "epic"
            assert epic_node["status"] == "draft"
            assert epic_node["document_id"] == str(epic_doc_id)

            story_node = data["nodes"][1]
            assert story_node["id"] == str(story_id)
            assert story_node["type"] == "story"
            assert story_node["document_id"] == str(story_doc_id)

            # Verify edges structure
            assert "edges" in data
            assert len(data["edges"]) == 1
            edge = data["edges"][0]
            assert edge["source_id"] == str(epic_id)
            assert edge["target_id"] == str(story_id)
            assert edge["type"] == "contains"
