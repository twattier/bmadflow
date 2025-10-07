"""Integration tests for file tree API endpoint."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.document import Document
from app.models.project import Project
from app.models.project_doc import ProjectDoc


@pytest.mark.asyncio
async def test_get_file_tree_success(db_session: AsyncSession):
    """Test successful file tree retrieval with nested structure."""
    # Arrange: Create project
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Test project for file tree",
    )
    db_session.add(project)
    await db_session.commit()

    # Create ProjectDoc
    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Test Repo",
        github_url="https://github.com/test/repo",
        github_folder_path="docs",
    )
    db_session.add(project_doc)
    await db_session.commit()

    # Create documents with nested structure
    documents = [
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc.id,
            file_path="docs/architecture.md",
            file_type="md",
            file_size=1000,
            content="# Architecture",
            doc_metadata={},
        ),
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc.id,
            file_path="docs/prd.md",
            file_type="md",
            file_size=2000,
            content="# PRD",
            doc_metadata={},
        ),
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc.id,
            file_path="docs/architecture/backend.md",
            file_type="md",
            file_size=1500,
            content="# Backend",
            doc_metadata={},
        ),
    ]
    for doc in documents:
        db_session.add(doc)
    await db_session.commit()

    # Act: Call API endpoint
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/projects/{project.id}/file-tree")

        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["project_id"] == str(project.id)
        assert "tree" in data
        assert len(data["tree"]) == 1  # One root folder: "docs"

        # Verify "docs" folder
        docs_folder = data["tree"][0]
        assert docs_folder["type"] == "folder"
        assert docs_folder["name"] == "docs"
        assert docs_folder["path"] == "docs"
        assert len(docs_folder["children"]) == 3  # "architecture" folder + 2 files

        # Verify nested structure (folders first, then files, alphabetically)
        assert docs_folder["children"][0]["type"] == "folder"
        assert docs_folder["children"][0]["name"] == "architecture"
        assert docs_folder["children"][1]["type"] == "file"
        assert docs_folder["children"][1]["name"] == "architecture.md"
        assert docs_folder["children"][2]["type"] == "file"
        assert docs_folder["children"][2]["name"] == "prd.md"


@pytest.mark.asyncio
async def test_get_file_tree_empty_project(db_session: AsyncSession):
    """Test file tree for project with no documents."""
    # Arrange: Create project with no documents
    project = Project(
        id=uuid.uuid4(),
        name="Empty Project",
        description="Project with no documents",
    )
    db_session.add(project)
    await db_session.commit()

    # Act: Call API endpoint
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/projects/{project.id}/file-tree")

        # Assert: Verify empty tree
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == str(project.id)
        assert data["tree"] == []


@pytest.mark.asyncio
async def test_get_file_tree_sorting(db_session: AsyncSession):
    """Test that folders come before files and all are sorted alphabetically."""
    # Arrange: Create project with mixed files and folders
    project = Project(
        id=uuid.uuid4(),
        name="Sorting Test Project",
        description="Test sorting",
    )
    db_session.add(project)
    await db_session.commit()

    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Test Repo",
        github_url="https://github.com/test/repo",
        github_folder_path="docs",
    )
    db_session.add(project_doc)
    await db_session.commit()

    # Create documents (intentionally unordered)
    documents = [
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc.id,
            file_path="zebra.md",
            file_type="md",
            file_size=100,
            content="Zebra",
            doc_metadata={},
        ),
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc.id,
            file_path="banana/file.md",
            file_type="md",
            file_size=100,
            content="Banana",
            doc_metadata={},
        ),
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc.id,
            file_path="apple/file.md",
            file_type="md",
            file_size=100,
            content="Apple",
            doc_metadata={},
        ),
        Document(
            id=uuid.uuid4(),
            project_doc_id=project_doc.id,
            file_path="aardvark.md",
            file_type="md",
            file_size=100,
            content="Aardvark",
            doc_metadata={},
        ),
    ]
    for doc in documents:
        db_session.add(doc)
    await db_session.commit()

    # Act: Call API endpoint
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/projects/{project.id}/file-tree")

        # Assert: Verify sorting (folders first, then files, alphabetically)
        assert response.status_code == 200
        data = response.json()
        tree = data["tree"]

        assert len(tree) == 4
        # Folders first (alphabetical)
        assert tree[0]["type"] == "folder"
        assert tree[0]["name"] == "apple"
        assert tree[1]["type"] == "folder"
        assert tree[1]["name"] == "banana"
        # Then files (alphabetical)
        assert tree[2]["type"] == "file"
        assert tree[2]["name"] == "aardvark.md"
        assert tree[3]["type"] == "file"
        assert tree[3]["name"] == "zebra.md"
