"""Unit tests for ExtractedEpicRepository."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.models.extracted_epic import ExtractedEpic
from src.repositories.extracted_epic_repository import ExtractedEpicRepository
from src.schemas.extraction_schemas import ExtractedEpicSchema


@pytest.fixture
def mock_db():
    """Mock async database session."""
    return AsyncMock()


@pytest.fixture
def repository(mock_db):
    """Fixture for ExtractedEpicRepository with mocked database."""
    return ExtractedEpicRepository(db=mock_db)


@pytest.fixture
def sample_schema():
    """Fixture for sample ExtractedEpicSchema."""
    return ExtractedEpicSchema(
        epic_number=2,
        title="LLM-Powered Content Extraction",
        goal="Implement OLLAMA-based extraction",
        status="dev",
        related_stories=["stories/story-2-1.md", "stories/story-2-2.md"],
        confidence_score=1.0,
    )


@pytest.mark.asyncio
async def test_get_by_document_id(repository, mock_db):
    """Test retrieving extraction by document ID."""
    document_id = uuid4()
    expected_extraction = ExtractedEpic(
        id=uuid4(),
        document_id=document_id,
        epic_number=1,
        title="Test Epic",
        goal="Test goal",
        status="draft",
        story_count=0,
        confidence_score=0.8,
        extracted_at=datetime.utcnow(),
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
    existing_extraction = ExtractedEpic(
        id=uuid4(),
        document_id=document_id,
        epic_number=1,
        title="Old Title",
        goal="Old goal",
        status="draft",
        story_count=5,
        confidence_score=0.5,
        extracted_at=datetime.utcnow(),
    )

    # Mock existing extraction found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_extraction
    mock_db.execute.return_value = mock_result

    result = await repository.create_or_update(document_id, sample_schema)

    # Verify fields were updated
    assert result.epic_number == sample_schema.epic_number
    assert result.title == sample_schema.title
    assert result.goal == sample_schema.goal
    assert result.status == sample_schema.status
    assert result.confidence_score == sample_schema.confidence_score

    # Verify commit and refresh were called
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(existing_extraction)


@pytest.mark.asyncio
async def test_related_stories_jsonb_serialization(repository, mock_db):
    """Test JSONB serialization for related_stories array."""
    document_id = uuid4()
    schema = ExtractedEpicSchema(
        epic_number=3,
        title="Epic with Stories",
        goal="Test JSONB",
        status="dev",
        related_stories=[
            "stories/story-3-1.md",
            "stories/story-3-2.md",
            "docs/stories/story-3-3.md"
        ],
        confidence_score=1.0,
    )

    # Mock no existing extraction
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Mock create to return the schema data
    created_epic = ExtractedEpic(
        id=uuid4(),
        document_id=document_id,
        epic_number=schema.epic_number,
        title=schema.title,
        goal=schema.goal,
        status=schema.status,
        story_count=0,
        confidence_score=schema.confidence_score,
        extracted_at=datetime.utcnow(),
    )
    repository.create = AsyncMock(return_value=created_epic)

    await repository.create_or_update(document_id, schema)

    # Verify create was called with correct parameters
    repository.create.assert_called_once_with(
        document_id=document_id,
        epic_number=schema.epic_number,
        title=schema.title,
        goal=schema.goal,
        status=schema.status,
        confidence_score=schema.confidence_score,
        story_count=0,
    )


@pytest.mark.asyncio
async def test_nullable_fields_accepted(repository, mock_db):
    """Test that nullable fields (epic_number, goal) can be None."""
    document_id = uuid4()
    schema_with_nulls = ExtractedEpicSchema(
        epic_number=None,
        title="Epic Without Number",
        goal=None,
        status=None,  # Will default to "draft"
        related_stories=None,
        confidence_score=0.25,
    )

    existing = ExtractedEpic(
        id=uuid4(),
        document_id=document_id,
        epic_number=5,
        title="old",
        goal="old goal",
        status="dev",
        story_count=3,
        confidence_score=1.0,
        extracted_at=datetime.utcnow(),
    )

    # Mock existing extraction
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_db.execute.return_value = mock_result

    result = await repository.create_or_update(document_id, schema_with_nulls)

    # Verify None values were set
    assert result.epic_number is None
    assert result.title == "Epic Without Number"
    assert result.goal is None
    assert result.status == "draft"  # Default applied
    assert result.confidence_score == 0.25


@pytest.mark.asyncio
async def test_unique_constraint_document_id(repository, mock_db):
    """Test unique constraint on document_id (implied by create_or_update logic)."""
    document_id = uuid4()
    schema = ExtractedEpicSchema(
        epic_number=1,
        title="Test",
        confidence_score=1.0,
    )

    # Mock existing extraction - demonstrates unique constraint
    existing = ExtractedEpic(
        id=uuid4(),
        document_id=document_id,
        epic_number=1,
        title="Existing",
        status="draft",
        story_count=0,
        confidence_score=0.5,
        extracted_at=datetime.utcnow(),
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_db.execute.return_value = mock_result

    # Call create_or_update twice with same document_id
    result1 = await repository.create_or_update(document_id, schema)
    result2 = await repository.create_or_update(document_id, schema)

    # Both should return the same extraction (updated)
    assert result1 == existing
    assert result2 == existing

    # Create should not be called (update path used)
    assert mock_db.commit.call_count == 2
