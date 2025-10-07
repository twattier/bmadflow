"""Integration tests for full sync workflow with real database."""

import time
import uuid
from datetime import datetime, timezone

import httpx
import pytest
import respx
from sqlalchemy import select

from app.models.document import Document
from app.models.project import Project
from app.models.project_doc import ProjectDoc


@pytest.mark.asyncio
@pytest.mark.respx(base_url="https://api.github.com")
async def test_sync_project_doc_full_workflow(db_session, respx_mock):
    """
    Test full sync workflow with real database and mocked GitHub API.

    This test verifies AC9: trigger sync via API, verify all files downloaded and stored.
    Uses test repository: https://github.com/twattier/bmadflow.git, folder: docs
    """
    # Arrange: Create test Project and ProjectDoc in database
    db = db_session

    # Create Project
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="Integration test project",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Create ProjectDoc
    project_doc = ProjectDoc(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Test Documentation",
        description="Integration test documentation",
        github_url="https://github.com/twattier/bmadflow.git",
        github_folder_path="docs",
    )
    db.add(project_doc)
    await db.commit()
    await db.refresh(project_doc)

    project_doc_id = project_doc.id

    # Mock GitHub API responses using respx

    @respx.mock
    async def run_sync_test():
        # Mock GitHub tree API (10+ files from docs folder)
        mock_files = [
            {"path": "docs/prd.md", "sha": "abc123", "type": "blob"},
            {"path": "docs/architecture.md", "sha": "def456", "type": "blob"},
            {"path": "docs/ux-specification.md", "sha": "ghi789", "type": "blob"},
            {"path": "docs/stories/1.1.md", "sha": "jkl012", "type": "blob"},
            {"path": "docs/stories/1.2.md", "sha": "mno345", "type": "blob"},
            {"path": "docs/stories/1.3.md", "sha": "pqr678", "type": "blob"},
            {"path": "docs/stories/1.4.md", "sha": "stu901", "type": "blob"},
            {"path": "docs/stories/1.5.md", "sha": "vwx234", "type": "blob"},
            {"path": "docs/stories/1.6.md", "sha": "yza567", "type": "blob"},
            {"path": "docs/epics/epic-1.md", "sha": "bcd890", "type": "blob"},
        ]

        # Mock tree API for both main and master branches
        respx.get("https://api.github.com/repos/twattier/bmadflow/git/trees/main").mock(
            return_value=httpx.Response(404, json={"message": "Not Found"})
        )

        respx.get("https://api.github.com/repos/twattier/bmadflow/git/trees/master").mock(
            return_value=httpx.Response(
                200,
                json={"tree": mock_files},
                headers={
                    "X-RateLimit-Remaining": "4999",
                    "X-RateLimit-Limit": "5000",
                    "X-RateLimit-Reset": str(int(time.time()) + 3600),
                },
            )
        )

        # Mock raw content downloads for each file
        for file_info in mock_files:
            file_path = file_info["path"]
            respx.get(f"https://raw.githubusercontent.com/twattier/bmadflow/main/{file_path}").mock(
                return_value=httpx.Response(404, text="Not Found")
            )

            respx.get(
                f"https://raw.githubusercontent.com/twattier/bmadflow/master/{file_path}"
            ).mock(
                return_value=httpx.Response(
                    200,
                    text=f"# Content of {file_path}\n\nTest content for integration test.",
                    headers={
                        "X-RateLimit-Remaining": "4998",
                        "X-RateLimit-Limit": "5000",
                        "X-RateLimit-Reset": str(int(time.time()) + 3600),
                    },
                )
            )

        # Mock commits API for last commit date
        respx.get("https://api.github.com/repos/twattier/bmadflow/commits").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "sha": "commit123",
                        "commit": {
                            "committer": {"date": "2025-01-15T10:30:00Z"},
                        },
                    }
                ],
                headers={
                    "X-RateLimit-Remaining": "4997",
                    "X-RateLimit-Limit": "5000",
                    "X-RateLimit-Reset": str(int(time.time()) + 3600),
                },
            )
        )

        # Act: Trigger sync via API endpoint
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(f"/api/project-docs/{project_doc_id}/sync")

        # Assert: Verify 202 Accepted response
        assert response.status_code == 202
        response_data = response.json()
        assert response_data["status"] == "processing"
        assert response_data["project_doc_id"] == str(project_doc_id)

        # Wait for background task completion with polling (10s timeout)
        max_wait = 10
        poll_interval = 0.5
        elapsed = 0
        documents_found = False

        while elapsed < max_wait:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            # Check if documents have been stored
            result = await db.execute(
                select(Document).where(Document.project_doc_id == project_doc_id)
            )
            documents = result.scalars().all()

            if len(documents) >= 10:
                documents_found = True
                break

        # Assert: Verify 10+ documents stored
        assert documents_found, f"Expected 10+ documents, found {len(documents)}"
        assert len(documents) == 10, f"Expected exactly 10 documents, found {len(documents)}"

        # Verify document details
        for doc in documents:
            assert doc.project_doc_id == project_doc_id
            assert doc.file_path.startswith("docs/")
            assert doc.content is not None
            assert len(doc.content) > 0
            assert doc.commit_sha is not None

        # Verify ProjectDoc timestamps updated
        result = await db.execute(select(ProjectDoc).where(ProjectDoc.id == project_doc_id))
        updated_project_doc = result.scalar_one()

        assert updated_project_doc.last_synced_at is not None
        assert updated_project_doc.last_synced_at.tzinfo is not None  # Timezone-aware
        assert updated_project_doc.last_github_commit_date is not None
        assert updated_project_doc.last_github_commit_date.tzinfo is not None

        # Verify timestamps are reasonable
        assert updated_project_doc.last_synced_at >= datetime(2025, 1, 1, tzinfo=timezone.utc)
        assert updated_project_doc.last_github_commit_date == datetime(
            2025, 1, 15, 10, 30, tzinfo=timezone.utc
        )

    # Run the mocked test
    await run_sync_test()
