"""Integration tests for extraction validation tool."""

import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import validation classes
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from validate_extraction import (
    AccuracyCalculator,
    ExtractedDataFetcher,
    validate_extraction,
)

from src.models.document import Document
from src.models.extracted_epic import ExtractedEpic
from src.models.extracted_story import ExtractedStory


@pytest.mark.asyncio
async def test_validate_sample_project(db_session: AsyncSession):
    """Integration test: validate extraction on a small test project."""
    # Create test project documents
    doc1 = Document(
        id=uuid4(),
        project_id=999,
        file_path="docs/stories/test-story-1.md",
        doc_type="story",
        content="# Test Story 1\n\nAs a backend developer, I want to configure OLLAMA",
    )
    doc2 = Document(
        id=uuid4(),
        project_id=999,
        file_path="docs/epics/test-epic-1.md",
        doc_type="epic",
        content="# Test Epic 1\n\nGoal: Setup infrastructure",
    )

    db_session.add(doc1)
    db_session.add(doc2)
    await db_session.flush()

    # Create extracted data
    story1 = ExtractedStory(
        id=uuid4(),
        document_id=doc1.id,
        role="backend developer",
        action="configure OLLAMA",
        benefit="extraction works",
        status="done",
        acceptance_criteria=["AC1", "AC2"],
        confidence_score=0.95,
    )
    epic1 = ExtractedEpic(
        id=uuid4(),
        document_id=doc2.id,
        epic_number=1,
        title="Test Epic",
        goal="Setup infrastructure",
        status="done",
        story_count=5,
        confidence_score=0.90,
    )

    db_session.add(story1)
    db_session.add(epic1)
    await db_session.commit()

    # Create ground truth CSV files
    story_csv = """document_id,expected_role,expected_action,expected_benefit,expected_status,expected_ac_count
docs/stories/test-story-1.md,backend developer,configure OLLAMA,extraction works,done,2
"""
    epic_csv = """document_id,expected_title,expected_goal,expected_status,expected_story_count
docs/epics/test-epic-1.md,Test Epic,Setup infrastructure,done,5
"""

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as story_f:
        story_f.write(story_csv)
        story_path = Path(story_f.name)

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as epic_f:
        epic_f.write(epic_csv)
        epic_path = Path(epic_f.name)

    try:
        # Run validation
        report = await validate_extraction(999, story_path, epic_path)

        # Assertions
        assert report.total_documents == 2
        assert report.fully_correct == 2
        assert report.partially_correct == 0
        assert report.failed == 0

        # Check field accuracy
        assert "role" in report.story_field_accuracy
        assert report.story_field_accuracy["role"][0] == 1  # 1 exact match

        assert "title" in report.epic_field_accuracy
        assert report.epic_field_accuracy["title"][0] == 1  # 1 exact match
    finally:
        story_path.unlink()
        epic_path.unlink()


@pytest.mark.asyncio
async def test_missing_extracted_document(db_session: AsyncSession):
    """Test handling when ground truth references missing extracted data."""
    # Create ground truth for non-existent document
    story_csv = """document_id,expected_role,expected_action,expected_benefit,expected_status,expected_ac_count
docs/stories/missing-story.md,backend developer,do something,achieve goal,done,3
"""

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(story_csv)
        csv_path = Path(f.name)

    try:
        # Run validation (should handle missing document gracefully)
        report = await validate_extraction(999, csv_path, None)

        # Should have 0 comparisons (document not found)
        assert report.total_documents == 0
    finally:
        csv_path.unlink()


@pytest.mark.asyncio
async def test_partial_match_scenario(db_session: AsyncSession):
    """Test scenario where extraction has partial matches."""
    doc = Document(
        id=uuid4(),
        project_id=888,
        file_path="docs/stories/partial-story.md",
        doc_type="story",
        content="# Partial Match Story",
    )
    db_session.add(doc)
    await db_session.flush()

    # Extracted data with slight variations
    story = ExtractedStory(
        id=uuid4(),
        document_id=doc.id,
        role="senior backend developer",  # Extra word
        action="configure OLLAMA LLM service",  # Extra words
        benefit="extraction pipeline works correctly",  # Extra words
        status="done",
        acceptance_criteria=["AC1", "AC2", "AC3"],  # 3 instead of 5
        confidence_score=0.85,
    )
    db_session.add(story)
    await db_session.commit()

    # Ground truth with exact expected values
    story_csv = """document_id,expected_role,expected_action,expected_benefit,expected_status,expected_ac_count
docs/stories/partial-story.md,backend developer,configure OLLAMA service,extraction works correctly,done,5
"""

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(story_csv)
        csv_path = Path(f.name)

    try:
        report = await validate_extraction(888, csv_path, None)

        # Should have 1 partially correct document (status exact, role/action partial, AC miss)
        assert report.total_documents == 1
        assert report.partially_correct == 1

        # Check specific field matches
        story_comp = report.comparisons[0]
        role_match = next(fc for fc in story_comp.field_comparisons if fc.field_name == "role")
        # "senior backend developer" vs "backend developer" = 66% overlap (2/3) - should be partial or miss depending on threshold
        assert role_match.match_type in ["partial", "miss"]

        status_match = next(fc for fc in story_comp.field_comparisons if fc.field_name == "status")
        assert status_match.match_type == "exact"

        ac_match = next(fc for fc in story_comp.field_comparisons if fc.field_name == "ac_count")
        assert ac_match.match_type == "miss"  # 3 != 5
    finally:
        csv_path.unlink()
