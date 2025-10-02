"""Unit tests for ExtractedStoryRepository."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.models.extracted_story import ExtractedStory
from src.repositories.extracted_story_repository import ExtractedStoryRepository
from src.schemas.extraction_schemas import ExtractedStorySchema


@pytest.fixture
def mock_db():
    """Mock async database session."""
    return AsyncMock()


@pytest.fixture
def repository(mock_db):
    """Fixture for ExtractedStoryRepository with mocked database."""
    return ExtractedStoryRepository(db=mock_db)


@pytest.fixture
def sample_schema():
    """Fixture for sample ExtractedStorySchema."""
    return ExtractedStorySchema(
        role="backend developer",
        action="implement feature",
        benefit="users have better experience",
        acceptance_criteria=["AC1", "AC2", "AC3"],
        status="draft",
        confidence_score=1.0,
    )


@pytest.mark.asyncio
async def test_get_by_document_id(repository, mock_db):
    """Test retrieving extraction by document ID."""
    document_id = uuid4()
    expected_extraction = ExtractedStory(
        id=uuid4(),
        document_id=document_id,
        role="developer",
        action="test",
        benefit="verify",
        acceptance_criteria=["AC1"],
        status="draft",
        confidence_score=0.8,
        created_at=datetime.utcnow(),
    )

    # Mock database result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_extraction
    mock_db.execute.return_value = mock_result

    result = await repository.get_by_document_id(document_id)

    assert result == expected_extraction
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_document_id_not_found(repository, mock_db):
    """Test get_by_document_id returns None when not found."""
    document_id = uuid4()

    # Mock empty result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await repository.get_by_document_id(document_id)

    assert result is None
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_or_update_updates_existing(repository, mock_db, sample_schema):
    """Test create_or_update updates existing extraction."""
    document_id = uuid4()
    existing_extraction = ExtractedStory(
        id=uuid4(),
        document_id=document_id,
        role="old role",
        action="old action",
        benefit="old benefit",
        acceptance_criteria=["Old AC"],
        status="dev",
        confidence_score=0.5,
        created_at=datetime.utcnow(),
    )

    # Mock existing extraction found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_extraction
    mock_db.execute.return_value = mock_result

    result = await repository.create_or_update(document_id, sample_schema)

    # Verify fields were updated
    assert result.role == sample_schema.role
    assert result.action == sample_schema.action
    assert result.benefit == sample_schema.benefit
    assert result.acceptance_criteria == sample_schema.acceptance_criteria
    assert result.status == sample_schema.status
    assert result.confidence_score == sample_schema.confidence_score

    # Verify commit and refresh were called
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(existing_extraction)


@pytest.mark.asyncio
async def test_nullable_fields_accepted(repository, mock_db):
    """Test that nullable fields can be None."""
    document_id = uuid4()
    schema_with_nulls = ExtractedStorySchema(
        role=None,
        action=None,
        benefit=None,
        acceptance_criteria=None,
        status=None,
        confidence_score=0.0,
    )

    existing = ExtractedStory(
        id=uuid4(),
        document_id=document_id,
        role="old",
        action="old",
        benefit="old",
        acceptance_criteria=["old"],
        status="draft",
        confidence_score=1.0,
        created_at=datetime.utcnow(),
    )

    # Mock existing extraction
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_db.execute.return_value = mock_result

    result = await repository.create_or_update(document_id, schema_with_nulls)

    # Verify None values were set
    assert result.role is None
    assert result.action is None
    assert result.benefit is None
    assert result.acceptance_criteria is None
    assert result.status is None
    assert result.confidence_score == 0.0
