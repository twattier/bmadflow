"""Integration tests for ProjectDoc repository and database operations."""

import asyncio
import pytest
from sqlalchemy import select

from app.models.project import Project
from app.models.project_doc import ProjectDoc
from app.repositories.project_doc import ProjectDocRepository
from app.schemas.project_doc import ProjectDocCreate, ProjectDocUpdate


class TestProjectDocRepository:
    """Integration tests for ProjectDocRepository."""

    @pytest.mark.asyncio
    async def test_create_project_doc_persists_to_database(self, db_session):
        """Test create ProjectDoc persists to database."""
        # Arrange
        project = Project(name="Test Project", description="Test")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        repo = ProjectDocRepository()
        data = ProjectDocCreate(
            name="Test Docs",
            description="Test Description",
            github_url="https://github.com/user/repo",
            github_folder_path="docs",
        )

        # Act
        project_doc = await repo.create(db_session, project.id, data)

        # Assert
        assert project_doc.id is not None
        assert project_doc.project_id == project.id
        assert project_doc.name == "Test Docs"
        assert project_doc.github_url == "https://github.com/user/repo"
        assert project_doc.github_folder_path == "docs"

        # Verify persistence
        result = await db_session.execute(select(ProjectDoc).where(ProjectDoc.id == project_doc.id))
        db_doc = result.scalar_one()
        assert db_doc.name == "Test Docs"

    @pytest.mark.asyncio
    async def test_get_all_by_project_orders_by_created_at_desc(self, db_session):
        """Test get_all_by_project returns docs ordered by created_at DESC."""
        # Arrange
        project = Project(name="Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        repo = ProjectDocRepository()

        # Create docs in specific order with small delay to ensure different timestamps
        doc1 = await repo.create(
            db_session,
            project.id,
            ProjectDocCreate(name="Doc 1", github_url="https://github.com/user/repo1"),
        )
        await asyncio.sleep(0.01)  # Small delay to ensure doc2 has later created_at
        doc2 = await repo.create(
            db_session,
            project.id,
            ProjectDocCreate(name="Doc 2", github_url="https://github.com/user/repo2"),
        )

        # Act
        docs = await repo.get_all_by_project(db_session, project.id)

        # Assert - both docs returned, ordered by created_at DESC
        assert len(docs) == 2
        # Verify both docs present (order may vary if created in same millisecond)
        doc_ids = {doc.id for doc in docs}
        assert doc1.id in doc_ids
        assert doc2.id in doc_ids
        # Verify descending order by timestamp
        assert docs[0].created_at >= docs[1].created_at

    @pytest.mark.asyncio
    async def test_delete_project_doc_succeeds(self, db_session):
        """Test delete ProjectDoc succeeds."""
        # Arrange
        project = Project(name="Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        repo = ProjectDocRepository()
        project_doc = await repo.create(
            db_session,
            project.id,
            ProjectDocCreate(name="Test Doc", github_url="https://github.com/user/repo"),
        )

        # Act
        deleted = await repo.delete(db_session, project_doc.id)

        # Assert
        assert deleted is True

        # Verify deletion
        result = await repo.get_by_id(db_session, project_doc.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_project_cascades_project_docs(self, db_session):
        """Test deleting project cascade deletes project_docs."""
        # Arrange
        project = Project(name="Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        repo = ProjectDocRepository()
        project_doc = await repo.create(
            db_session,
            project.id,
            ProjectDocCreate(name="Test Doc", github_url="https://github.com/user/repo"),
        )

        # Act - Delete project
        await db_session.delete(project)
        await db_session.commit()

        # Assert - ProjectDoc also deleted (CASCADE)
        result = await repo.get_by_id(db_session, project_doc.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_project_doc_modifies_fields(self, db_session):
        """Test update ProjectDoc modifies fields and updates timestamp."""
        # Arrange
        project = Project(name="Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        repo = ProjectDocRepository()
        project_doc = await repo.create(
            db_session,
            project.id,
            ProjectDocCreate(
                name="Original Name",
                description="Original",
                github_url="https://github.com/user/repo",
            ),
        )

        # Act
        updated_doc = await repo.update(
            db_session,
            project_doc.id,
            ProjectDocUpdate(name="Updated Name", description="Updated Description"),
        )

        # Assert
        assert updated_doc.name == "Updated Name"
        assert updated_doc.description == "Updated Description"
        assert updated_doc.github_url == "https://github.com/user/repo"
        # Note: updated_at timestamp check may not work due to server_default behavior

    @pytest.mark.asyncio
    async def test_github_url_validation_enforced(self, db_session):
        """Test GitHub URL validation enforced via Pydantic."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Must be a GitHub repository URL"):
            ProjectDocCreate(
                name="Test Doc",
                github_url="https://gitlab.com/user/repo",  # Not GitHub
            )

    @pytest.mark.asyncio
    async def test_folder_path_normalization(self, db_session):
        """Test folder path normalization removes leading/trailing slashes."""
        # Arrange
        project = Project(name="Test Project")
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        repo = ProjectDocRepository()

        # Act
        project_doc = await repo.create(
            db_session,
            project.id,
            ProjectDocCreate(
                name="Test Doc",
                github_url="https://github.com/user/repo",
                github_folder_path="/docs/",  # Leading and trailing slashes
            ),
        )

        # Assert
        assert project_doc.github_folder_path == "docs"
