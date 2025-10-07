"""Integration tests for Project API with real database."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


@pytest.mark.asyncio
async def test_create_project_persists_to_database(db_session: AsyncSession):
    """Test create project persists to database."""
    # Arrange
    repo = ProjectRepository()
    project_data = ProjectCreate(name="Test Project", description="Integration Test")

    # Act
    project = await repo.create(db_session, project_data)

    # Assert
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "Integration Test"
    assert project.created_at is not None
    assert project.updated_at is not None


@pytest.mark.asyncio
async def test_get_project_by_id_from_database(db_session: AsyncSession):
    """Test get project by ID from database."""
    # Arrange
    repo = ProjectRepository()
    created_project = await repo.create(
        db_session, ProjectCreate(name="Retrieve Test", description="Test Retrieval")
    )

    # Act
    retrieved_project = await repo.get_by_id(db_session, created_project.id)

    # Assert
    assert retrieved_project is not None
    assert retrieved_project.id == created_project.id
    assert retrieved_project.name == "Retrieve Test"


@pytest.mark.asyncio
async def test_update_project_in_database(db_session: AsyncSession):
    """Test update project updates in database."""
    # Arrange
    repo = ProjectRepository()
    project = await repo.create(
        db_session, ProjectCreate(name="Original Name", description="Original")
    )

    # Act
    updated_project = await repo.update(
        db_session,
        project.id,
        ProjectUpdate(name="Updated Name", description="Updated Desc"),
    )

    # Assert
    assert updated_project is not None
    assert updated_project.name == "Updated Name"
    assert updated_project.description == "Updated Desc"
    assert updated_project.updated_at > updated_project.created_at


@pytest.mark.asyncio
async def test_delete_project_removes_from_database(db_session: AsyncSession):
    """Test delete project removes from database."""
    # Arrange
    repo = ProjectRepository()
    project = await repo.create(
        db_session, ProjectCreate(name="To Delete", description="Will be deleted")
    )
    project_id = project.id

    # Act
    deleted = await repo.delete(db_session, project_id)

    # Assert
    assert deleted is True
    retrieved = await repo.get_by_id(db_session, project_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_list_projects_orders_by_created_at_desc(db_session: AsyncSession):
    """Test list projects returns projects ordered by created_at DESC."""
    # Arrange
    repo = ProjectRepository()
    project1 = await repo.create(db_session, ProjectCreate(name="Project 1", description="First"))
    project2 = await repo.create(db_session, ProjectCreate(name="Project 2", description="Second"))

    # Act
    projects = await repo.get_all(db_session)

    # Assert
    assert len(projects) >= 2
    # Most recently created should be first
    project_ids = [p.id for p in projects]
    assert project2.id in project_ids
    assert project1.id in project_ids
    # Verify order (newer first)
    project2_index = project_ids.index(project2.id)
    project1_index = project_ids.index(project1.id)
    assert project2_index < project1_index


@pytest.mark.asyncio
async def test_database_constraints_enforced(db_session: AsyncSession):
    """Test database constraints enforced (NOT NULL on name)."""
    # Act & Assert - Cannot create project without name
    # Pydantic will catch this before database, but let's verify database would reject too
    from sqlalchemy.exc import IntegrityError

    project = Project()
    project.description = "No name"
    db_session.add(project)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()
