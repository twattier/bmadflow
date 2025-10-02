"""Simplified integration tests for project API routes."""

import pytest
from src.services.sync_service import detect_doc_type


def test_detect_doc_type_patterns():
    """Test all doc_type detection patterns."""
    test_cases = [
        ("docs/prd/overview.md", "scoping"),
        ("docs/architecture/tech-stack.md", "architecture"),
        ("docs/epics/epic-1.md", "epic"),
        ("docs/stories/story-1.1.md", "story"),
        ("docs/qa/test-plan.md", "qa"),
        ("README.md", "other"),
        ("/docs/prd/overview.md", "scoping"),
        ("/docs/architecture/tech-stack.md", "architecture"),
    ]

    for file_path, expected_type in test_cases:
        assert detect_doc_type(file_path) == expected_type, f"Failed for {file_path}"


def test_doc_type_case_insensitive():
    """Test that doc_type detection is case insensitive."""
    assert detect_doc_type("DOCS/PRD/OVERVIEW.MD") == "scoping"
    assert detect_doc_type("Docs/Architecture/Backend.md") == "architecture"
