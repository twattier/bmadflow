"""Integration test for status detection validation on 20-document test set."""

import pytest
import csv
import os
from pathlib import Path
from unittest.mock import Mock

from src.services.story_extraction_service import StoryExtractionService
from src.models.document import Document


@pytest.fixture
def extraction_service():
    """Fixture for real StoryExtractionService (no mocking for integration test)."""
    return StoryExtractionService()


@pytest.fixture
def test_fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures" / "status_detection"


def load_ground_truth(fixtures_dir):
    """Load ground truth CSV data."""
    ground_truth = {}
    csv_path = fixtures_dir / "ground_truth.csv"

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ground_truth[row['filename']] = row['expected_status']

    return ground_truth


@pytest.mark.asyncio
@pytest.mark.integration
async def test_status_detection_validation_explicit_markers(extraction_service, test_fixtures_dir):
    """
    Validate status detection on 10 documents with explicit markers.
    Target: ≥90% accuracy (AC 6).
    """
    ground_truth = load_ground_truth(test_fixtures_dir)

    explicit_files = [f for f in ground_truth.keys() if f.startswith('explicit_')]

    correct = 0
    total = len(explicit_files)
    results = []

    for filename in explicit_files:
        file_path = test_fixtures_dir / filename
        expected_status = ground_truth[filename]

        # Read document content
        with open(file_path, 'r') as f:
            content = f.read()

        # Create mock document
        doc = Mock(spec=Document)
        doc.id = filename
        doc.content = content

        # Extract status (this will use LLM if OLLAMA is running, else regex fallback)
        result = await extraction_service.extract_story(doc)

        match = result.status == expected_status
        if match:
            correct += 1

        results.append({
            'filename': filename,
            'expected': expected_status,
            'extracted': result.status,
            'match': match
        })

    accuracy = (correct / total) * 100

    # Print results for debugging
    print(f"\n=== Explicit Markers Validation ===")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"\nDetailed Results:")
    for r in results:
        status = "✓" if r['match'] else "✗"
        print(f"  {status} {r['filename']}: expected={r['expected']}, extracted={r['extracted']}")

    # Assert AC 6 requirement: ≥90% accuracy on explicit markers
    assert accuracy >= 90.0, \
        f"Explicit marker accuracy {accuracy:.1f}% below target 90%"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_status_detection_validation_inference(extraction_service, test_fixtures_dir):
    """
    Validate status detection on 10 documents requiring inference.
    Target: ≥70% accuracy (AC 6).
    """
    ground_truth = load_ground_truth(test_fixtures_dir)

    inference_files = [f for f in ground_truth.keys() if f.startswith('inference_')]

    correct = 0
    total = len(inference_files)
    results = []

    for filename in inference_files:
        file_path = test_fixtures_dir / filename
        expected_status = ground_truth[filename]

        # Read document content
        with open(file_path, 'r') as f:
            content = f.read()

        # Create mock document
        doc = Mock(spec=Document)
        doc.id = filename
        doc.content = content

        # Extract status (this will use LLM inference)
        result = await extraction_service.extract_story(doc)

        match = result.status == expected_status
        if match:
            correct += 1

        results.append({
            'filename': filename,
            'expected': expected_status,
            'extracted': result.status,
            'match': match
        })

    accuracy = (correct / total) * 100

    # Print results for debugging
    print(f"\n=== Inference Validation ===")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"\nDetailed Results:")
    for r in results:
        status = "✓" if r['match'] else "✗"
        print(f"  {status} {r['filename']}: expected={r['expected']}, extracted={r['extracted']}")

    # Assert AC 6 requirement: ≥70% accuracy on inference
    assert accuracy >= 70.0, \
        f"Inference accuracy {accuracy:.1f}% below target 70%"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_status_detection_validation_all_documents(extraction_service, test_fixtures_dir):
    """
    Validate status detection on all 20 documents.
    Provides overall accuracy report.
    """
    ground_truth = load_ground_truth(test_fixtures_dir)

    correct = 0
    total = len(ground_truth)
    results = []

    for filename, expected_status in ground_truth.items():
        file_path = test_fixtures_dir / filename

        # Read document content
        with open(file_path, 'r') as f:
            content = f.read()

        # Create mock document
        doc = Mock(spec=Document)
        doc.id = filename
        doc.content = content

        # Extract status
        result = await extraction_service.extract_story(doc)

        match = result.status == expected_status
        if match:
            correct += 1

        results.append({
            'filename': filename,
            'expected': expected_status,
            'extracted': result.status,
            'match': match,
            'confidence': result.confidence_score
        })

    accuracy = (correct / total) * 100

    # Print comprehensive report
    print(f"\n=== Overall Status Detection Validation ===")
    print(f"Total Documents: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"\nDetailed Results:")
    for r in results:
        status = "✓" if r['match'] else "✗"
        print(f"  {status} {r['filename']}: expected={r['expected']}, extracted={r['extracted']}, confidence={r['confidence']:.2f}")

    # Overall success: Expect high accuracy across all documents
    assert accuracy >= 80.0, \
        f"Overall accuracy {accuracy:.1f}% below expected threshold"
