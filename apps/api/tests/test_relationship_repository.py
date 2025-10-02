"""Unit tests for RelationshipRepository."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.models.relationship import Relationship
from src.repositories.relationship_repository import RelationshipRepository


@pytest.fixture
def mock_db():
    """Mock async database session."""
    return AsyncMock()


@pytest.fixture
def repository(mock_db):
    """Fixture for RelationshipRepository with mocked database."""
    return RelationshipRepository(db=mock_db)


@pytest.mark.asyncio
async def test_create_relationship_success(repository, mock_db):
    """Test creating a relationship with valid parent and child document IDs."""
    parent_id = uuid4()
    child_id = uuid4()

    # Mock successful create
    created_relationship = Relationship(
        id=uuid4(),
        parent_doc_id=parent_id,
        child_doc_id=child_id,
        relationship_type="contains",
        created_at=datetime.utcnow(),
    )
    repository.create = AsyncMock(return_value=created_relationship)

    result = await repository.create_relationship(parent_id, child_id, "contains")

    assert result == created_relationship
    repository.create.assert_called_once_with(
        parent_doc_id=parent_id,
        child_doc_id=child_id,
        relationship_type="contains",
    )


@pytest.mark.asyncio
async def test_create_relationship_duplicate_handling(repository, mock_db):
    """Test duplicate relationship handling (unique constraint)."""
    parent_id = uuid4()
    child_id = uuid4()

    # Mock IntegrityError (unique constraint violation)
    repository.create = AsyncMock(side_effect=IntegrityError("", "", ""))

    result = await repository.create_relationship(parent_id, child_id, "contains")

    # Should return None on duplicate
    assert result is None
    # Should rollback transaction
    mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_parent_doc_id_returns_all_children(repository, mock_db):
    """Test get_by_parent_doc_id returns all child relationships."""
    parent_id = uuid4()
    child1_id = uuid4()
    child2_id = uuid4()
    child3_id = uuid4()

    relationships = [
        Relationship(
            id=uuid4(),
            parent_doc_id=parent_id,
            child_doc_id=child1_id,
            relationship_type="contains",
            created_at=datetime.utcnow(),
        ),
        Relationship(
            id=uuid4(),
            parent_doc_id=parent_id,
            child_doc_id=child2_id,
            relationship_type="contains",
            created_at=datetime.utcnow(),
        ),
        Relationship(
            id=uuid4(),
            parent_doc_id=parent_id,
            child_doc_id=child3_id,
            relationship_type="contains",
            created_at=datetime.utcnow(),
        ),
    ]

    # Mock database result
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = relationships
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    result = await repository.get_by_parent_doc_id(parent_id)

    assert len(result) == 3
    assert all(r.parent_doc_id == parent_id for r in result)
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_parent_doc_id_empty_result(repository, mock_db):
    """Test get_by_parent_doc_id returns empty list when no relationships."""
    parent_id = uuid4()

    # Mock empty result
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    result = await repository.get_by_parent_doc_id(parent_id)

    assert result == []
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_relationship_type_parameter(repository, mock_db):
    """Test relationship_type parameter is respected."""
    parent_id = uuid4()
    child_id = uuid4()

    created_relationship = Relationship(
        id=uuid4(),
        parent_doc_id=parent_id,
        child_doc_id=child_id,
        relationship_type="relates_to",
        created_at=datetime.utcnow(),
    )
    repository.create = AsyncMock(return_value=created_relationship)

    result = await repository.create_relationship(parent_id, child_id, "relates_to")

    assert result.relationship_type == "relates_to"
    repository.create.assert_called_once_with(
        parent_doc_id=parent_id,
        child_doc_id=child_id,
        relationship_type="relates_to",
    )


@pytest.mark.asyncio
async def test_default_relationship_type_contains(repository, mock_db):
    """Test default relationship_type is 'contains'."""
    parent_id = uuid4()
    child_id = uuid4()

    created_relationship = Relationship(
        id=uuid4(),
        parent_doc_id=parent_id,
        child_doc_id=child_id,
        relationship_type="contains",
        created_at=datetime.utcnow(),
    )
    repository.create = AsyncMock(return_value=created_relationship)

    # Call without relationship_type parameter
    result = await repository.create_relationship(parent_id, child_id)

    assert result.relationship_type == "contains"
