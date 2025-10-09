"""Integration tests for Document sync workflow."""

from datetime import datetime

import httpx
import pytest
import respx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.project import Project
from app.models.project_doc import ProjectDoc
from app.repositories.document_repository import DocumentRepository
from app.schemas.github import FileInfo
from app.services.document_service import DocumentService
from app.services.github_service import GitHubService


@pytest.fixture
async def test_project(db_session: AsyncSession) -> Project:
    """Create a test project."""
    project = Project(
        name="Test BMADFlow Project",
        description="Integration test project for document sync",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
async def test_project_doc(db_session: AsyncSession, test_project: Project) -> ProjectDoc:
    """Create a test project doc."""
    project_doc = ProjectDoc(
        project_id=test_project.id,
        name="Test Documentation",
        description="Test docs for sync",
        github_url="https://github.com/test-user/test-repo",
        github_folder_path="docs",
    )
    db_session.add(project_doc)
    await db_session.commit()
    await db_session.refresh(project_doc)
    return project_doc


@pytest.mark.asyncio
@respx.mock
async def test_sync_documents_from_github(db_session: AsyncSession, test_project_doc: ProjectDoc):
    """Test full document sync workflow with 10+ files."""
    # Arrange: Mock GitHub API responses for 12 files
    file_contents = {
        "docs/README.md": "# Test README\n\nThis is a test readme.",
        "docs/prd.md": "# Product Requirements\n\nPRD content here.",
        "docs/architecture.md": "# Architecture\n\nArchitecture docs.",
        "docs/api-spec.yaml": "openapi: 3.0.0\ninfo:\n  title: Test API",
        "docs/data.csv": "id,name,value\n1,test,100\n2,demo,200",
        "docs/config.json": '{"setting1": "value1", "setting2": "value2"}',
        "docs/notes.txt": "Some plain text notes for testing.",
        "docs/setup.md": "# Setup Guide\n\nInstallation instructions.",
        "docs/changelog.md": "# Changelog\n\n## v1.0.0\n- Initial release",
        "docs/contributing.md": "# Contributing\n\nHow to contribute.",
        "docs/license.md": "# License\n\nMIT License details.",
        "docs/faq.yml": "questions:\n  - q: What?\n    a: This is a test",
    }

    # Mock raw content URLs for all files
    for file_path, content in file_contents.items():
        respx.get(f"https://raw.githubusercontent.com/test-user/test-repo/main/{file_path}").mock(
            return_value=httpx.Response(
                200,
                text=content,
                headers={
                    "X-RateLimit-Remaining": "4999",
                    "X-RateLimit-Limit": "5000",
                    "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
                },
            )
        )

        # Mock GitHub API contents endpoint for SHA
        file_name = file_path.split("/")[-1]
        respx.get(f"https://api.github.com/repos/test-user/test-repo/contents/{file_path}").mock(
            return_value=httpx.Response(
                200,
                json={
                    "name": file_name,
                    "path": file_path,
                    "sha": f"sha{hash(file_path) % 1000000}",
                    "size": len(content),
                    "type": "file",
                },
                headers={
                    "X-RateLimit-Remaining": "4998",
                    "X-RateLimit-Limit": "5000",
                    "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + 3600),
                },
            )
        )

    # Create services
    document_repo = DocumentRepository(db_session)
    document_service = DocumentService(document_repo)
    github_service = GitHubService()

    # Prepare file list with FileInfo objects
    files_to_sync = []
    for file_path, content in file_contents.items():
        file_info = FileInfo(
            path=file_path,
            sha=f"sha{hash(file_path) % 1000000}",
            type="blob",
            size=len(content),
        )
        # Download content
        downloaded_content, commit_sha = await github_service.download_file_content(
            test_project_doc.github_url, file_path
        )
        files_to_sync.append((file_info, downloaded_content, commit_sha))

    # Act: Sync documents
    stored_docs = await document_service.store_documents_batch(test_project_doc.id, files_to_sync)

    # Assert: Verify all files stored
    assert len(stored_docs) == 12, "Should store all 12 files"

    # Verify documents in database
    result = await db_session.execute(
        select(Document).where(Document.project_doc_id == test_project_doc.id)
    )
    db_documents = list(result.scalars().all())

    assert len(db_documents) == 12, "Should have 12 documents in database"

    # Verify each document has correct fields
    for doc in db_documents:
        assert doc.project_doc_id == test_project_doc.id
        assert doc.file_path in file_contents
        assert doc.content == file_contents[doc.file_path]
        assert doc.file_size == len(file_contents[doc.file_path])
        assert doc.file_type in ["md", "yaml", "yml", "csv", "json", "txt"]
        assert doc.doc_metadata is not None
        assert "github_commit_sha" in doc.doc_metadata
        assert doc.created_at is not None
        assert doc.updated_at is not None

    # Test upsert logic: Run sync twice, verify no duplicates
    stored_docs_second = await document_service.store_documents_batch(
        test_project_doc.id, files_to_sync
    )

    assert len(stored_docs_second) == 12, "Should still store all 12 files on re-sync"

    # Verify still only 12 documents (no duplicates)
    result = await db_session.execute(
        select(Document).where(Document.project_doc_id == test_project_doc.id)
    )
    db_documents_after_resync = list(result.scalars().all())

    assert (
        len(db_documents_after_resync) == 12
    ), "Should still have exactly 12 documents (no duplicates)"

    # Verify file_path uniqueness
    file_paths = {doc.file_path for doc in db_documents_after_resync}
    assert len(file_paths) == 12, "All file paths should be unique"

    # Verify file type distribution
    file_types = [doc.file_type for doc in db_documents_after_resync]
    assert "md" in file_types  # Markdown files
    assert "csv" in file_types  # CSV file
    assert "yaml" in file_types or "yml" in file_types  # YAML files
    assert "json" in file_types  # JSON file
    assert "txt" in file_types  # Text file


@pytest.mark.asyncio
async def test_document_cascade_delete(db_session: AsyncSession, test_project_doc: ProjectDoc):
    """Test that documents are deleted when ProjectDoc is deleted."""
    # Arrange: Create some test documents
    doc1 = Document(
        project_doc_id=test_project_doc.id,
        file_path="test/file1.md",
        file_type="md",
        file_size=100,
        content="Test content 1",
        doc_metadata={"github_commit_sha": "abc123"},
    )
    doc2 = Document(
        project_doc_id=test_project_doc.id,
        file_path="test/file2.md",
        file_type="md",
        file_size=200,
        content="Test content 2",
        doc_metadata={"github_commit_sha": "def456"},
    )
    db_session.add(doc1)
    db_session.add(doc2)
    await db_session.commit()

    # Verify documents exist
    result = await db_session.execute(
        select(Document).where(Document.project_doc_id == test_project_doc.id)
    )
    docs_before = list(result.scalars().all())
    assert len(docs_before) == 2

    # Act: Delete ProjectDoc
    await db_session.delete(test_project_doc)
    await db_session.commit()

    # Assert: Documents should be cascade deleted
    result = await db_session.execute(
        select(Document).where(Document.project_doc_id == test_project_doc.id)
    )
    docs_after = list(result.scalars().all())
    assert len(docs_after) == 0, "Documents should be cascade deleted with ProjectDoc"
