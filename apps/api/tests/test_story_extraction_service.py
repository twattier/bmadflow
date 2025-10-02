"""Unit tests for StoryExtractionService."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from src.services.story_extraction_service import StoryExtractionService
from src.models.document import Document
from src.schemas.extraction_schemas import ExtractedStorySchema


@pytest.fixture
def mock_ollama_service():
    """Fixture for mocked OLLAMA service."""
    return AsyncMock()


@pytest.fixture
def extraction_service(mock_ollama_service):
    """Fixture for StoryExtractionService with mocked OLLAMA."""
    return StoryExtractionService(ollama_service=mock_ollama_service)


@pytest.fixture
def sample_document():
    """Fixture for sample story document."""
    doc = Mock(spec=Document)
    doc.id = "123e4567-e89b-12d3-a456-426614174000"
    doc.content = """# Story 1.1: Project Setup

**Status:** Draft

## Story

**As a** backend developer,
**I want** to set up project infrastructure,
**so that** we have a working development environment.

## Acceptance Criteria

1. Docker Compose configuration created
2. Database migrations set up
3. FastAPI application running
4. Tests passing
"""
    return doc


@pytest.mark.asyncio
async def test_extract_story_success(extraction_service, mock_ollama_service, sample_document):
    """Test successful extraction with all fields populated."""
    # Mock OLLAMA response with complete data
    mock_ollama_service.generate.return_value = {
        "content": json.dumps({
            "role": "backend developer",
            "action": "to set up project infrastructure",
            "benefit": "we have a working development environment",
            "acceptance_criteria": [
                "Docker Compose configuration created",
                "Database migrations set up",
                "FastAPI application running",
                "Tests passing"
            ],
            "status": "draft"
        })
    }

    result = await extraction_service.extract_story(sample_document)

    assert isinstance(result, ExtractedStorySchema)
    assert result.role == "backend developer"
    assert result.action == "to set up project infrastructure"
    assert result.benefit == "we have a working development environment"
    assert len(result.acceptance_criteria) == 4
    assert result.status == "draft"
    assert result.confidence_score == 1.0  # All 5 fields present


@pytest.mark.asyncio
async def test_extract_story_partial_data(extraction_service, mock_ollama_service, sample_document):
    """Test extraction with missing fields (partial data)."""
    # Mock OLLAMA response with missing benefit and status
    mock_ollama_service.generate.return_value = {
        "content": json.dumps({
            "role": "backend developer",
            "action": "to set up project infrastructure",
            "benefit": None,
            "acceptance_criteria": [
                "Docker Compose configuration created",
                "Database migrations set up"
            ],
            "status": None
        })
    }

    result = await extraction_service.extract_story(sample_document)

    assert result.role == "backend developer"
    assert result.action == "to set up project infrastructure"
    assert result.benefit is None
    assert len(result.acceptance_criteria) == 2
    assert result.status is None
    assert result.confidence_score == 0.6  # 3 fields present


@pytest.mark.asyncio
async def test_extract_story_llm_error(extraction_service, mock_ollama_service, sample_document):
    """Test extraction failure handling when OLLAMA times out."""
    # Mock OLLAMA to raise exception
    mock_ollama_service.generate.side_effect = Exception("OLLAMA timeout")

    result = await extraction_service.extract_story(sample_document)

    assert isinstance(result, ExtractedStorySchema)
    assert result.role is None
    assert result.action is None
    assert result.benefit is None
    assert result.acceptance_criteria is None
    assert result.status is None
    assert result.confidence_score == 0.0


@pytest.mark.asyncio
async def test_extract_story_json_parse_failure_with_regex_fallback(
    extraction_service, mock_ollama_service, sample_document
):
    """Test JSON parse failure with regex fallback."""
    # Mock OLLAMA to return malformed JSON
    mock_ollama_service.generate.return_value = {
        "content": "This is not JSON at all!"
    }

    result = await extraction_service.extract_story(sample_document)

    # Regex fallback should extract at least some fields from sample_document.content
    assert isinstance(result, ExtractedStorySchema)
    assert result.role == "backend developer"  # Extracted via regex
    assert result.confidence_score > 0.0  # Some fields found


@pytest.mark.asyncio
async def test_confidence_score_calculation(extraction_service, mock_ollama_service, sample_document):
    """Test confidence score calculation with different field counts."""
    test_cases = [
        (0, 0.0),  # 0 fields
        (1, 0.2),  # 1 field
        (2, 0.4),  # 2 fields
        (3, 0.6),  # 3 fields
        (4, 0.8),  # 4 fields
        (5, 1.0),  # 5 fields (all)
    ]

    for field_count, expected_confidence in test_cases:
        data = {
            "role": "developer" if field_count >= 1 else None,
            "action": "do something" if field_count >= 2 else None,
            "benefit": "achieve goal" if field_count >= 3 else None,
            "acceptance_criteria": ["AC1"] if field_count >= 4 else None,
            "status": "draft" if field_count >= 5 else None,
        }

        mock_ollama_service.generate.return_value = {
            "content": json.dumps(data)
        }

        result = await extraction_service.extract_story(sample_document)
        assert result.confidence_score == expected_confidence, \
            f"Expected confidence {expected_confidence} for {field_count} fields, got {result.confidence_score}"


@pytest.mark.asyncio
async def test_status_normalization(extraction_service, mock_ollama_service, sample_document):
    """Test status normalization to lowercase enum values."""
    status_test_cases = [
        ("Draft", "draft"),
        ("DRAFT", "draft"),
        ("Dev", "dev"),
        ("DEV", "dev"),
        ("Done", "done"),
        ("DONE", "done"),
        ("invalid", None),  # Invalid status normalized to None
        (None, None),
    ]

    for input_status, expected_status in status_test_cases:
        mock_ollama_service.generate.return_value = {
            "content": json.dumps({
                "role": "developer",
                "action": "test",
                "benefit": "verify",
                "acceptance_criteria": ["AC1"],
                "status": input_status
            })
        }

        result = await extraction_service.extract_story(sample_document)
        assert result.status == expected_status, \
            f"Expected status '{expected_status}' for input '{input_status}', got '{result.status}'"


@pytest.mark.asyncio
async def test_regex_fallback_extracts_basic_fields(extraction_service):
    """Test regex fallback can extract basic fields from markdown."""
    doc = Mock(spec=Document)
    doc.id = "test-id"
    doc.content = """
**As a** developer,
**I want** to test regex,
**so that** extraction works.

**Status:** Dev

1. First AC
2. Second AC
"""

    # Force JSON parse failure
    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_story(doc)

        assert result.role == "developer"  # Regex strips trailing comma
        assert result.action is not None  # Should extract action
        assert result.status == "dev"
        assert result.acceptance_criteria == ["First AC", "Second AC"]


@pytest.mark.asyncio
async def test_ollama_called_with_json_format(extraction_service, mock_ollama_service, sample_document):
    """Test that OLLAMA is called with format_json=True."""
    mock_ollama_service.generate.return_value = {
        "content": json.dumps({
            "role": "dev",
            "action": "test",
            "benefit": "verify",
            "acceptance_criteria": [],
            "status": "draft"
        })
    }

    await extraction_service.extract_story(sample_document)

    mock_ollama_service.generate.assert_called_once()
    call_args = mock_ollama_service.generate.call_args
    assert call_args[1]["format_json"] is True
    assert "BMAD markdown story analyzer" in call_args[1]["system_prompt"]


@pytest.mark.asyncio
async def test_empty_acceptance_criteria_handled(extraction_service, mock_ollama_service, sample_document):
    """Test that empty acceptance criteria array is handled correctly."""
    mock_ollama_service.generate.return_value = {
        "content": json.dumps({
            "role": "developer",
            "action": "test",
            "benefit": "verify",
            "acceptance_criteria": [],  # Empty array
            "status": "draft"
        })
    }

    result = await extraction_service.extract_story(sample_document)

    assert result.acceptance_criteria == []
    # Empty array counts as "not populated" for confidence
    assert result.confidence_score == 0.8  # 4 fields (role, action, benefit, status)


# Story 2.4: Status Detection Enhancement Tests


@pytest.mark.asyncio
async def test_explicit_status_bold_format(extraction_service):
    """Test status detection with bold format: **Status:** Draft."""
    doc = Mock(spec=Document)
    doc.id = "test-bold"
    doc.content = """
# Story 1.1

**Status:** Draft

**As a** developer,
**I want** to test,
**so that** it works.
"""

    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_story(doc)
        assert result.status == "draft"


@pytest.mark.asyncio
async def test_explicit_status_plain_format(extraction_service):
    """Test status detection with plain format: Status: Dev."""
    doc = Mock(spec=Document)
    doc.id = "test-plain"
    doc.content = """
# Story 1.2

Status: Dev

**As a** developer,
**I want** to test,
**so that** it works.
"""

    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_story(doc)
        assert result.status == "dev"


@pytest.mark.asyncio
async def test_explicit_status_bracketed_format(extraction_service):
    """Test status detection with bracketed format: [Status: Done]."""
    doc = Mock(spec=Document)
    doc.id = "test-bracketed"
    doc.content = """
# Story 1.3

[Status: Done]

**As a** developer,
**I want** to test,
**so that** it works.
"""

    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_story(doc)
        assert result.status == "done"


@pytest.mark.asyncio
async def test_explicit_status_html_comment_format(extraction_service):
    """Test status detection with HTML comment: <!-- status: dev -->."""
    doc = Mock(spec=Document)
    doc.id = "test-html"
    doc.content = """
# Story 1.4

<!-- status: dev -->

**As a** developer,
**I want** to test,
**so that** it works.
"""

    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_story(doc)
        assert result.status == "dev"


@pytest.mark.asyncio
async def test_status_case_insensitive(extraction_service):
    """Test that status detection is case-insensitive."""
    test_cases = [
        ("**STATUS:** DRAFT", "draft"),
        ("Status: DEV", "dev"),
        ("[Status: DONE]", "done"),
        ("<!-- STATUS: DRAFT -->", "draft"),
    ]

    for content_status, expected in test_cases:
        doc = Mock(spec=Document)
        doc.id = f"test-case-{expected}"
        doc.content = f"""
# Story

{content_status}

**As a** developer,
**I want** to test,
**so that** it works.
"""

        with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
            result = await extraction_service.extract_story(doc)
            assert result.status == expected, f"Expected {expected} for {content_status}"


@pytest.mark.asyncio
async def test_regex_fallback_tries_all_patterns(extraction_service):
    """Test that regex fallback tries all status patterns in order."""
    # Test pattern priority: bold > plain > bracketed > html comment
    doc_with_multiple = Mock(spec=Document)
    doc_with_multiple.id = "test-multiple"
    doc_with_multiple.content = """
# Story

**Status:** Draft
Status: Dev
[Status: Done]

**As a** developer,
**I want** to test,
**so that** it works.
"""

    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_story(doc_with_multiple)
        # Should match first pattern (bold)
        assert result.status == "draft"


@pytest.mark.asyncio
async def test_status_normalization_to_lowercase(extraction_service, mock_ollama_service, sample_document):
    """Test that all status values are normalized to lowercase enum."""
    test_cases = ["DRAFT", "Draft", "draft", "DEV", "Dev", "dev", "DONE", "Done", "done"]

    for input_status in test_cases:
        mock_ollama_service.generate.return_value = {
            "content": json.dumps({
                "role": "developer",
                "action": "test",
                "benefit": "verify",
                "acceptance_criteria": ["AC1"],
                "status": input_status
            })
        }

        result = await extraction_service.extract_story(sample_document)
        assert result.status in ["draft", "dev", "done"], \
            f"Status {input_status} should normalize to draft/dev/done"
        assert result.status == input_status.lower()


@pytest.mark.asyncio
async def test_status_inference_not_in_regex(extraction_service):
    """Test that LLM inference is used when no explicit markers exist (regex returns None)."""
    doc_no_marker = Mock(spec=Document)
    doc_no_marker.id = "test-inference"
    doc_no_marker.content = """
# Story

**As a** developer,
**I want** to test inference,
**so that** it works correctly.

## Tasks
- [x] All tasks complete
- [x] Everything done
"""

    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_story(doc_no_marker)
        # Regex won't find status, returns None
        assert result.status is None  # Regex fallback has no inference logic
