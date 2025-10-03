#!/usr/bin/env python3
"""
Extraction Accuracy Validation Tool

Compares LLM-extracted data against ground truth CSV to measure extraction accuracy.

Usage:
    python scripts/validate_extraction.py --project-id 1 --ground-truth test_data/ground_truth.csv
"""

import argparse
import asyncio
import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from uuid import UUID

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.models.document import Document
from src.models.extracted_epic import ExtractedEpic
from src.models.extracted_story import ExtractedStory


@dataclass
class GroundTruthStory:
    """Ground truth data for a user story."""

    document_id: str
    expected_role: Optional[str]
    expected_action: Optional[str]
    expected_benefit: Optional[str]
    expected_status: Optional[str]
    expected_ac_count: Optional[int]


@dataclass
class GroundTruthEpic:
    """Ground truth data for an epic."""

    document_id: str
    expected_title: Optional[str]
    expected_goal: Optional[str]
    expected_status: Optional[str]
    expected_story_count: Optional[int]


@dataclass
class FieldComparison:
    """Comparison result for a single field."""

    field_name: str
    extracted_value: Optional[str]
    expected_value: Optional[str]
    match_type: str  # "exact", "partial", "miss", "n/a"


@dataclass
class DocumentComparison:
    """Comparison result for an entire document."""

    document_id: str
    document_type: str  # "story" or "epic"
    field_comparisons: List[FieldComparison]
    overall_match: str  # "fully_correct", "partially_correct", "failed"


@dataclass
class AccuracyReport:
    """Overall accuracy metrics."""

    total_documents: int
    fully_correct: int
    partially_correct: int
    failed: int
    story_field_accuracy: Dict[str, Tuple[int, int, int]]  # field -> (exact, partial, miss)
    epic_field_accuracy: Dict[str, Tuple[int, int, int]]
    comparisons: List[DocumentComparison]


class StringMatcher:
    """Utilities for comparing extracted vs expected strings."""

    @staticmethod
    def normalize(text: Optional[str]) -> str:
        """Normalize string for comparison (lowercase, strip, remove extra whitespace)."""
        if not text:
            return ""
        return " ".join(text.lower().strip().split())

    @staticmethod
    def exact_match(extracted: Optional[str], expected: Optional[str]) -> bool:
        """Check if two strings match exactly after normalization."""
        return StringMatcher.normalize(extracted) == StringMatcher.normalize(expected)

    @staticmethod
    def partial_match(extracted: Optional[str], expected: Optional[str], threshold: float = 0.7) -> bool:
        """Check if extracted string has 70%+ word overlap with expected."""
        if not extracted or not expected:
            return False

        extracted_words = set(StringMatcher.normalize(extracted).split())
        expected_words = set(StringMatcher.normalize(expected).split())

        if not expected_words:
            return False

        overlap = len(extracted_words & expected_words)
        return (overlap / len(expected_words)) >= threshold

    @staticmethod
    def compare(extracted: Optional[str], expected: Optional[str]) -> str:
        """Compare two strings and return match type."""
        if expected is None:
            return "n/a"
        if StringMatcher.exact_match(extracted, expected):
            return "exact"
        if StringMatcher.partial_match(extracted, expected):
            return "partial"
        return "miss"


class GroundTruthLoader:
    """Loads ground truth data from CSV files."""

    @staticmethod
    def load_stories(csv_path: Path) -> List[GroundTruthStory]:
        """Load story ground truth from CSV."""
        stories = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stories.append(
                    GroundTruthStory(
                        document_id=row["document_id"],
                        expected_role=row.get("expected_role") or None,
                        expected_action=row.get("expected_action") or None,
                        expected_benefit=row.get("expected_benefit") or None,
                        expected_status=row.get("expected_status") or None,
                        expected_ac_count=int(row["expected_ac_count"]) if row.get("expected_ac_count") else None,
                    )
                )
        return stories

    @staticmethod
    def load_epics(csv_path: Path) -> List[GroundTruthEpic]:
        """Load epic ground truth from CSV."""
        epics = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                epics.append(
                    GroundTruthEpic(
                        document_id=row["document_id"],
                        expected_title=row.get("expected_title") or None,
                        expected_goal=row.get("expected_goal") or None,
                        expected_status=row.get("expected_status") or None,
                        expected_story_count=int(row["expected_story_count"]) if row.get("expected_story_count") else None,
                    )
                )
        return epics


class ExtractedDataFetcher:
    """Fetches extracted data from database."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_stories(self, project_id: int) -> List[Tuple[Document, ExtractedStory]]:
        """Fetch all extracted stories for a project."""
        query = (
            select(Document, ExtractedStory)
            .join(ExtractedStory, Document.id == ExtractedStory.document_id)
            .where(Document.project_id == project_id)
            .where(Document.doc_type == "story")
        )
        result = await self.session.execute(query)
        return result.all()

    async def fetch_epics(self, project_id: int) -> List[Tuple[Document, ExtractedEpic]]:
        """Fetch all extracted epics for a project."""
        query = (
            select(Document, ExtractedEpic)
            .join(ExtractedEpic, Document.id == ExtractedEpic.document_id)
            .where(Document.project_id == project_id)
            .where(Document.doc_type == "epic")
        )
        result = await self.session.execute(query)
        return result.all()


class StoryComparator:
    """Compares extracted stories against ground truth."""

    @staticmethod
    def compare(extracted: ExtractedStory, ground_truth: GroundTruthStory) -> DocumentComparison:
        """Compare extracted story with ground truth."""
        comparisons = []

        # Compare role
        comparisons.append(
            FieldComparison(
                field_name="role",
                extracted_value=extracted.role,
                expected_value=ground_truth.expected_role,
                match_type=StringMatcher.compare(extracted.role, ground_truth.expected_role),
            )
        )

        # Compare action
        comparisons.append(
            FieldComparison(
                field_name="action",
                extracted_value=extracted.action,
                expected_value=ground_truth.expected_action,
                match_type=StringMatcher.compare(extracted.action, ground_truth.expected_action),
            )
        )

        # Compare benefit
        comparisons.append(
            FieldComparison(
                field_name="benefit",
                extracted_value=extracted.benefit,
                expected_value=ground_truth.expected_benefit,
                match_type=StringMatcher.compare(extracted.benefit, ground_truth.expected_benefit),
            )
        )

        # Compare status
        comparisons.append(
            FieldComparison(
                field_name="status",
                extracted_value=extracted.status,
                expected_value=ground_truth.expected_status,
                match_type=StringMatcher.compare(extracted.status, ground_truth.expected_status),
            )
        )

        # Compare AC count
        extracted_ac_count = len(extracted.acceptance_criteria) if extracted.acceptance_criteria else 0
        ac_match = "n/a"
        if ground_truth.expected_ac_count is not None:
            ac_match = "exact" if extracted_ac_count == ground_truth.expected_ac_count else "miss"

        comparisons.append(
            FieldComparison(
                field_name="ac_count",
                extracted_value=str(extracted_ac_count),
                expected_value=str(ground_truth.expected_ac_count) if ground_truth.expected_ac_count else None,
                match_type=ac_match,
            )
        )

        # Determine overall match
        exact_matches = sum(1 for c in comparisons if c.match_type == "exact")
        partial_matches = sum(1 for c in comparisons if c.match_type == "partial")
        misses = sum(1 for c in comparisons if c.match_type == "miss")

        if exact_matches == len(comparisons):
            overall_match = "fully_correct"
        elif misses == len(comparisons):
            overall_match = "failed"
        else:
            overall_match = "partially_correct"

        return DocumentComparison(
            document_id=ground_truth.document_id,
            document_type="story",
            field_comparisons=comparisons,
            overall_match=overall_match,
        )


class EpicComparator:
    """Compares extracted epics against ground truth."""

    @staticmethod
    def compare(extracted: ExtractedEpic, ground_truth: GroundTruthEpic) -> DocumentComparison:
        """Compare extracted epic with ground truth."""
        comparisons = []

        # Compare title
        comparisons.append(
            FieldComparison(
                field_name="title",
                extracted_value=extracted.title,
                expected_value=ground_truth.expected_title,
                match_type=StringMatcher.compare(extracted.title, ground_truth.expected_title),
            )
        )

        # Compare goal
        comparisons.append(
            FieldComparison(
                field_name="goal",
                extracted_value=extracted.goal,
                expected_value=ground_truth.expected_goal,
                match_type=StringMatcher.compare(extracted.goal, ground_truth.expected_goal),
            )
        )

        # Compare status
        comparisons.append(
            FieldComparison(
                field_name="status",
                extracted_value=extracted.status,
                expected_value=ground_truth.expected_status,
                match_type=StringMatcher.compare(extracted.status, ground_truth.expected_status),
            )
        )

        # Compare story count
        story_match = "n/a"
        if ground_truth.expected_story_count is not None:
            story_match = "exact" if extracted.story_count == ground_truth.expected_story_count else "miss"

        comparisons.append(
            FieldComparison(
                field_name="story_count",
                extracted_value=str(extracted.story_count),
                expected_value=str(ground_truth.expected_story_count) if ground_truth.expected_story_count else None,
                match_type=story_match,
            )
        )

        # Determine overall match
        exact_matches = sum(1 for c in comparisons if c.match_type == "exact")
        partial_matches = sum(1 for c in comparisons if c.match_type == "partial")
        misses = sum(1 for c in comparisons if c.match_type == "miss")

        if exact_matches == len(comparisons):
            overall_match = "fully_correct"
        elif misses == len(comparisons):
            overall_match = "failed"
        else:
            overall_match = "partially_correct"

        return DocumentComparison(
            document_id=ground_truth.document_id,
            document_type="epic",
            field_comparisons=comparisons,
            overall_match=overall_match,
        )


class AccuracyCalculator:
    """Calculates accuracy metrics from comparisons."""

    @staticmethod
    def calculate(comparisons: List[DocumentComparison]) -> AccuracyReport:
        """Calculate overall accuracy report."""
        total = len(comparisons)
        fully_correct = sum(1 for c in comparisons if c.overall_match == "fully_correct")
        partially_correct = sum(1 for c in comparisons if c.overall_match == "partially_correct")
        failed = sum(1 for c in comparisons if c.overall_match == "failed")

        # Calculate per-field accuracy for stories
        story_comparisons = [c for c in comparisons if c.document_type == "story"]
        story_field_accuracy = AccuracyCalculator._calculate_field_accuracy(story_comparisons)

        # Calculate per-field accuracy for epics
        epic_comparisons = [c for c in comparisons if c.document_type == "epic"]
        epic_field_accuracy = AccuracyCalculator._calculate_field_accuracy(epic_comparisons)

        return AccuracyReport(
            total_documents=total,
            fully_correct=fully_correct,
            partially_correct=partially_correct,
            failed=failed,
            story_field_accuracy=story_field_accuracy,
            epic_field_accuracy=epic_field_accuracy,
            comparisons=comparisons,
        )

    @staticmethod
    def _calculate_field_accuracy(comparisons: List[DocumentComparison]) -> Dict[str, Tuple[int, int, int]]:
        """Calculate per-field accuracy (exact, partial, miss counts)."""
        field_stats = {}

        for comparison in comparisons:
            for field_comp in comparison.field_comparisons:
                if field_comp.field_name not in field_stats:
                    field_stats[field_comp.field_name] = [0, 0, 0]  # [exact, partial, miss]

                if field_comp.match_type == "exact":
                    field_stats[field_comp.field_name][0] += 1
                elif field_comp.match_type == "partial":
                    field_stats[field_comp.field_name][1] += 1
                elif field_comp.match_type == "miss":
                    field_stats[field_comp.field_name][2] += 1

        return {k: tuple(v) for k, v in field_stats.items()}


class ReportGenerator:
    """Generates markdown validation report."""

    @staticmethod
    def generate(report: AccuracyReport, project_id: int) -> str:
        """Generate markdown report from accuracy data."""
        overall_accuracy = (report.fully_correct / report.total_documents * 100) if report.total_documents > 0 else 0

        story_count = len([c for c in report.comparisons if c.document_type == "story"])
        epic_count = len([c for c in report.comparisons if c.document_type == "epic"])

        md = f"""# Extraction Validation Report

**Date:** {ReportGenerator._get_date()}
**Project ID:** {project_id}
**Test Set Size:** {report.total_documents} documents ({story_count} stories, {epic_count} epics)

## Overall Results

- **Total Documents:** {report.total_documents}
- **Fully Correct:** {report.fully_correct} ({report.fully_correct / report.total_documents * 100:.1f}%)
- **Partially Correct:** {report.partially_correct} ({report.partially_correct / report.total_documents * 100:.1f}%)
- **Failed:** {report.failed} ({report.failed / report.total_documents * 100:.1f}%)
- **Overall Accuracy:** {overall_accuracy:.1f}%

"""

        # Story extraction table
        if story_count > 0:
            md += f"## Story Extraction ({story_count} documents)\n\n"
            md += "| Field | Accuracy | Exact Matches | Partial Matches | Misses |\n"
            md += "|-------|----------|---------------|-----------------|--------|\n"

            for field, (exact, partial, miss) in report.story_field_accuracy.items():
                total = exact + partial + miss
                accuracy = (exact / total * 100) if total > 0 else 0
                md += f"| {field} | {accuracy:.1f}% | {exact} | {partial} | {miss} |\n"

            md += "\n"

        # Epic extraction table
        if epic_count > 0:
            md += f"## Epic Extraction ({epic_count} documents)\n\n"
            md += "| Field | Accuracy | Exact Matches | Partial Matches | Misses |\n"
            md += "|-------|----------|---------------|-----------------|--------|\n"

            for field, (exact, partial, miss) in report.epic_field_accuracy.items():
                total = exact + partial + miss
                accuracy = (exact / total * 100) if total > 0 else 0
                md += f"| {field} | {accuracy:.1f}% | {exact} | {partial} | {miss} |\n"

            md += "\n"

        # Failure analysis
        md += ReportGenerator._generate_failure_analysis(report)

        # Recommendations
        md += "\n## Recommendations\n\n"
        if overall_accuracy >= 90:
            md += f"- ✅ Overall accuracy {overall_accuracy:.1f}% exceeds 90% target - **no prompt engineering improvements needed**\n"
        else:
            md += f"- ⚠️ Overall accuracy {overall_accuracy:.1f}% below 90% target - **prompt engineering improvements recommended**\n"
            md += "- Review failure patterns above and implement Stories 2.7a/2.7c as needed\n"

        return md

    @staticmethod
    def _get_date() -> str:
        """Get current date in YYYY-MM-DD format."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _generate_failure_analysis(report: AccuracyReport) -> str:
        """Generate failure analysis section."""
        md = "## Failure Analysis\n\n"

        # Collect all failures
        failures = []
        for comp in report.comparisons:
            for field_comp in comp.field_comparisons:
                if field_comp.match_type == "miss":
                    failures.append((comp.document_type, field_comp.field_name, field_comp))

        if not failures:
            md += "No failures detected. All fields extracted successfully.\n"
            return md

        # Group by failure type
        failure_counts = {}
        for doc_type, field_name, field_comp in failures:
            key = f"{doc_type}.{field_name}"
            if key not in failure_counts:
                failure_counts[key] = []
            failure_counts[key].append(field_comp)

        # Sort by count (descending)
        sorted_failures = sorted(failure_counts.items(), key=lambda x: len(x[1]), reverse=True)

        md += "### Top Failure Patterns\n\n"
        for i, (key, field_comps) in enumerate(sorted_failures[:3], 1):
            count = len(field_comps)
            md += f"{i}. **{key} Mismatch ({count} cases):** Field extraction failed or did not match expected value\n"

        return md


async def validate_extraction(project_id: int, ground_truth_stories_path: Optional[Path], ground_truth_epics_path: Optional[Path]) -> AccuracyReport:
    """Main validation logic."""
    async with AsyncSessionLocal() as session:
        fetcher = ExtractedDataFetcher(session)

        all_comparisons = []

        # Validate stories
        if ground_truth_stories_path and ground_truth_stories_path.exists():
            ground_truth_stories = GroundTruthLoader.load_stories(ground_truth_stories_path)
            extracted_stories = await fetcher.fetch_stories(project_id)

            # Create lookup by file_path
            extracted_by_path = {doc.file_path: story for doc, story in extracted_stories}

            for gt in ground_truth_stories:
                if gt.document_id in extracted_by_path:
                    extracted = extracted_by_path[gt.document_id]
                    comparison = StoryComparator.compare(extracted, gt)
                    all_comparisons.append(comparison)
                else:
                    print(f"Warning: No extracted data found for story document_id={gt.document_id}")

        # Validate epics
        if ground_truth_epics_path and ground_truth_epics_path.exists():
            ground_truth_epics = GroundTruthLoader.load_epics(ground_truth_epics_path)
            extracted_epics = await fetcher.fetch_epics(project_id)

            # Create lookup by file_path
            extracted_by_path = {doc.file_path: epic for doc, epic in extracted_epics}

            for gt in ground_truth_epics:
                if gt.document_id in extracted_by_path:
                    extracted = extracted_by_path[gt.document_id]
                    comparison = EpicComparator.compare(extracted, gt)
                    all_comparisons.append(comparison)
                else:
                    print(f"Warning: No extracted data found for epic document_id={gt.document_id}")

        # Calculate accuracy
        return AccuracyCalculator.calculate(all_comparisons)


async def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate extraction accuracy against ground truth")
    parser.add_argument("--project-id", type=int, required=True, help="Project ID to validate")
    parser.add_argument("--ground-truth-stories", type=Path, help="Path to ground truth stories CSV")
    parser.add_argument("--ground-truth-epics", type=Path, help="Path to ground truth epics CSV")
    parser.add_argument("--output", type=Path, default=Path("docs/extraction-validation-results.md"), help="Output report path")

    args = parser.parse_args()

    if not args.ground_truth_stories and not args.ground_truth_epics:
        print("Error: At least one ground truth CSV file must be provided")
        sys.exit(1)

    print(f"Validating extraction for project {args.project_id}...")

    # Run validation
    report = await validate_extraction(args.project_id, args.ground_truth_stories, args.ground_truth_epics)

    # Check for zero documents
    if report.total_documents == 0:
        print("\n⚠️  Error: No documents found for validation.")
        print("Possible causes:")
        print("  - Project ID does not exist or has no extracted data")
        print("  - Ground truth document_id values don't match database file_path values")
        print("  - No extraction has been run for this project")
        print("\nPlease verify:")
        print("  1. Project has been synced and extraction completed")
        print("  2. Ground truth CSV document_id matches documents.file_path in database")
        sys.exit(1)

    # Generate markdown report
    markdown_report = ReportGenerator.generate(report, args.project_id)

    # Write report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print(f"\nValidation complete!")
    print(f"Total documents: {report.total_documents}")
    print(f"Fully correct: {report.fully_correct} ({report.fully_correct / report.total_documents * 100:.1f}%)")
    print(f"Partially correct: {report.partially_correct} ({report.partially_correct / report.total_documents * 100:.1f}%)")
    print(f"Failed: {report.failed} ({report.failed / report.total_documents * 100:.1f}%)")
    print(f"\nReport written to: {args.output}")

    # Exit with non-zero if accuracy below 90%
    overall_accuracy = (report.fully_correct / report.total_documents * 100) if report.total_documents > 0 else 0
    if overall_accuracy < 90:
        print("\n⚠️  Accuracy below 90% target. Consider implementing Stories 2.7a/2.7c.")
        sys.exit(1)
    else:
        print(f"\n✅ Accuracy {overall_accuracy:.1f}% meets 90% target!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
