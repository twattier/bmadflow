"""Unit tests for extraction validation tool."""

import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

import pytest

# Import validation classes from scripts
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from validate_extraction import (
    AccuracyCalculator,
    DocumentComparison,
    EpicComparator,
    FieldComparison,
    GroundTruthEpic,
    GroundTruthLoader,
    GroundTruthStory,
    ReportGenerator,
    StoryComparator,
    StringMatcher,
)

from src.models.extracted_epic import ExtractedEpic
from src.models.extracted_story import ExtractedStory


class TestStringMatcher:
    """Test string normalization and matching logic."""

    def test_normalize(self):
        """Test string normalization."""
        assert StringMatcher.normalize("  Hello   World  ") == "hello world"
        assert StringMatcher.normalize("Backend Developer") == "backend developer"
        assert StringMatcher.normalize("") == ""
        assert StringMatcher.normalize(None) == ""

    def test_exact_match(self):
        """Test exact match logic."""
        assert StringMatcher.exact_match("Backend Developer", "backend developer")
        assert StringMatcher.exact_match("  Test  ", "test")
        assert not StringMatcher.exact_match("Backend Dev", "Backend Developer")
        assert not StringMatcher.exact_match("abc", "xyz")

    def test_partial_match(self):
        """Test partial match with 70%+ word overlap."""
        # 100% overlap
        assert StringMatcher.partial_match("backend developer", "backend developer")

        # 66% overlap (2 out of 3 words) - should fail (below 70% threshold)
        assert not StringMatcher.partial_match(
            "backend developer engineer", "backend developer architect"
        )

        # 80% overlap (4 out of 5 words in expected)
        assert StringMatcher.partial_match(
            "configure OLLAMA LLM service", "configure OLLAMA LLM model"
        )

        # 50% overlap - should fail (below 70% threshold)
        assert not StringMatcher.partial_match("backend developer", "frontend engineer")

        # No overlap
        assert not StringMatcher.partial_match("abc", "xyz")

    def test_compare(self):
        """Test overall comparison logic."""
        assert StringMatcher.compare("test", "test") == "exact"
        assert StringMatcher.compare("  Test  ", "test") == "exact"
        assert StringMatcher.compare("configure OLLAMA LLM service", "configure OLLAMA LLM model") == "partial"
        assert StringMatcher.compare("backend developer", "backend engineer") == "miss"
        assert StringMatcher.compare("abc", "xyz") == "miss"
        assert StringMatcher.compare("test", None) == "n/a"


class TestGroundTruthLoader:
    """Test CSV loading for ground truth data."""

    def test_load_stories(self):
        """Test loading story ground truth from CSV."""
        csv_content = """document_id,expected_role,expected_action,expected_benefit,expected_status,expected_ac_count
docs/stories/story-1.md,backend developer,configure OLLAMA,extraction works,done,8
docs/stories/story-2.md,frontend developer,build UI,users can see dashboard,dev,5
"""
        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = Path(f.name)

        try:
            stories = GroundTruthLoader.load_stories(temp_path)

            assert len(stories) == 2
            assert stories[0].document_id == "docs/stories/story-1.md"
            assert stories[0].expected_role == "backend developer"
            assert stories[0].expected_action == "configure OLLAMA"
            assert stories[0].expected_status == "done"
            assert stories[0].expected_ac_count == 8

            assert stories[1].document_id == "docs/stories/story-2.md"
            assert stories[1].expected_ac_count == 5
        finally:
            temp_path.unlink()

    def test_load_epics(self):
        """Test loading epic ground truth from CSV."""
        csv_content = """document_id,expected_title,expected_goal,expected_status,expected_story_count
docs/epics/epic-1.md,Foundation,Setup infrastructure,done,8
docs/epics/epic-2.md,LLM Extraction,Extract structured data,in progress,9
"""
        with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = Path(f.name)

        try:
            epics = GroundTruthLoader.load_epics(temp_path)

            assert len(epics) == 2
            assert epics[0].document_id == "docs/epics/epic-1.md"
            assert epics[0].expected_title == "Foundation"
            assert epics[0].expected_status == "done"
            assert epics[0].expected_story_count == 8
        finally:
            temp_path.unlink()


class TestStoryComparator:
    """Test story comparison logic."""

    def test_compare_exact_match(self):
        """Test story comparison with all fields matching exactly."""
        extracted = ExtractedStory(
            id=uuid4(),
            document_id=uuid4(),
            role="backend developer",
            action="configure OLLAMA",
            benefit="extraction works",
            status="done",
            acceptance_criteria=["AC1", "AC2", "AC3"],
            confidence_score=0.95,
        )

        ground_truth = GroundTruthStory(
            document_id="docs/stories/story-1.md",
            expected_role="backend developer",
            expected_action="configure OLLAMA",
            expected_benefit="extraction works",
            expected_status="done",
            expected_ac_count=3,
        )

        comparison = StoryComparator.compare(extracted, ground_truth)

        assert comparison.overall_match == "fully_correct"
        assert len(comparison.field_comparisons) == 5
        assert all(fc.match_type == "exact" for fc in comparison.field_comparisons)

    def test_compare_partial_match(self):
        """Test story comparison with partial matches."""
        extracted = ExtractedStory(
            id=uuid4(),
            document_id=uuid4(),
            role="backend developer engineer",
            action="configure OLLAMA service",
            benefit="extraction pipeline works",
            status="done",
            acceptance_criteria=["AC1", "AC2"],
            confidence_score=0.90,
        )

        ground_truth = GroundTruthStory(
            document_id="docs/stories/story-1.md",
            expected_role="backend developer",
            expected_action="configure OLLAMA",
            expected_benefit="extraction works",
            expected_status="done",
            expected_ac_count=3,
        )

        comparison = StoryComparator.compare(extracted, ground_truth)

        # Should be partially correct (status exact, others partial/miss)
        assert comparison.overall_match == "partially_correct"

        # Check individual fields
        role_comp = next(fc for fc in comparison.field_comparisons if fc.field_name == "role")
        assert role_comp.match_type == "partial"

        status_comp = next(fc for fc in comparison.field_comparisons if fc.field_name == "status")
        assert status_comp.match_type == "exact"

        ac_comp = next(fc for fc in comparison.field_comparisons if fc.field_name == "ac_count")
        assert ac_comp.match_type == "miss"

    def test_compare_failed(self):
        """Test story comparison with all fields mismatched."""
        extracted = ExtractedStory(
            id=uuid4(),
            document_id=uuid4(),
            role="frontend developer",
            action="build UI",
            benefit="users see dashboard",
            status="dev",
            acceptance_criteria=["AC1"],
            confidence_score=0.80,
        )

        ground_truth = GroundTruthStory(
            document_id="docs/stories/story-1.md",
            expected_role="backend developer",
            expected_action="configure OLLAMA",
            expected_benefit="extraction works",
            expected_status="done",
            expected_ac_count=8,
        )

        comparison = StoryComparator.compare(extracted, ground_truth)

        # All fields mismatch = failed
        assert comparison.overall_match == "failed"


class TestEpicComparator:
    """Test epic comparison logic."""

    def test_compare_exact_match(self):
        """Test epic comparison with all fields matching exactly."""
        extracted = ExtractedEpic(
            id=uuid4(),
            document_id=uuid4(),
            epic_number=1,
            title="Foundation",
            goal="Setup infrastructure",
            status="done",
            story_count=8,
            confidence_score=0.95,
        )

        ground_truth = GroundTruthEpic(
            document_id="docs/epics/epic-1.md",
            expected_title="Foundation",
            expected_goal="Setup infrastructure",
            expected_status="done",
            expected_story_count=8,
        )

        comparison = EpicComparator.compare(extracted, ground_truth)

        assert comparison.overall_match == "fully_correct"
        assert len(comparison.field_comparisons) == 4
        assert all(fc.match_type == "exact" for fc in comparison.field_comparisons)


class TestAccuracyCalculator:
    """Test accuracy calculation."""

    def test_calculate_accuracy(self):
        """Test overall accuracy calculation."""
        comparisons = [
            DocumentComparison(
                document_id="doc1",
                document_type="story",
                field_comparisons=[
                    FieldComparison("role", "backend dev", "backend dev", "exact"),
                    FieldComparison("action", "config", "config", "exact"),
                ],
                overall_match="fully_correct",
            ),
            DocumentComparison(
                document_id="doc2",
                document_type="story",
                field_comparisons=[
                    FieldComparison("role", "backend dev", "backend dev", "exact"),
                    FieldComparison("action", "config service", "config", "partial"),
                ],
                overall_match="partially_correct",
            ),
            DocumentComparison(
                document_id="doc3",
                document_type="epic",
                field_comparisons=[
                    FieldComparison("title", "wrong", "right", "miss"),
                ],
                overall_match="failed",
            ),
        ]

        report = AccuracyCalculator.calculate(comparisons)

        assert report.total_documents == 3
        assert report.fully_correct == 1
        assert report.partially_correct == 1
        assert report.failed == 1

        # Check story field accuracy
        assert "role" in report.story_field_accuracy
        assert report.story_field_accuracy["role"] == (2, 0, 0)  # 2 exact, 0 partial, 0 miss

        assert "action" in report.story_field_accuracy
        assert report.story_field_accuracy["action"] == (1, 1, 0)  # 1 exact, 1 partial, 0 miss


class TestReportGenerator:
    """Test markdown report generation."""

    def test_generate_report(self):
        """Test report generation from accuracy data."""
        comparisons = [
            DocumentComparison(
                document_id="doc1",
                document_type="story",
                field_comparisons=[
                    FieldComparison("role", "backend dev", "backend dev", "exact"),
                    FieldComparison("action", "config", "config", "exact"),
                ],
                overall_match="fully_correct",
            ),
        ]

        report = AccuracyCalculator.calculate(comparisons)
        markdown = ReportGenerator.generate(report, project_id=1)

        # Check report contains key sections
        assert "# Extraction Validation Report" in markdown
        assert "**Project ID:** 1" in markdown
        assert "**Total Documents:** 1" in markdown
        assert "**Fully Correct:** 1" in markdown
        assert "**Overall Accuracy:** 100.0%" in markdown
        assert "## Story Extraction" in markdown
        assert "role" in markdown
        assert "action" in markdown
        assert "✅" in markdown  # Success indicator for 90%+ accuracy
