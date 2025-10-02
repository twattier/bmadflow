"""Unit tests for EpicExtractionService."""

import pytest
from unittest.mock import Mock, AsyncMock
import json

from src.services.epic_extraction_service import EpicExtractionService
from src.models.document import Document
from src.schemas.extraction_schemas import ExtractedEpicSchema


@pytest.fixture
def mock_ollama_service():
    """Fixture for mocked OLLAMA service."""
    return AsyncMock()


@pytest.fixture
def extraction_service(mock_ollama_service):
    """Fixture for EpicExtractionService with mocked OLLAMA."""
    return EpicExtractionService(ollama_service=mock_ollama_service)


@pytest.fixture
def sample_epic_document():
    """Fixture for sample epic document."""
    doc = Mock(spec=Document)
    doc.id = "epic-123e4567-e89b-12d3-a456-426614174000"
    doc.project_id = "proj-123e4567-e89b-12d3-a456-426614174000"
    doc.content = """# Epic 2: LLM-Powered Content Extraction

**Status:** Dev

## Epic Goal

Implement OLLAMA-based extraction of structured information from BMAD markdown.

## Stories

- [Story 2.1](stories/story-2-1.md)
- [Story 2.2](stories/story-2-2.md)
- [Story 2.3](docs/stories/story-2-3.md)
"""
    return doc


@pytest.mark.asyncio
async def test_extract_epic_success(extraction_service, mock_ollama_service, sample_epic_document):
    """Test successful extraction with all fields populated."""
    # Mock OLLAMA response with complete data
    mock_ollama_service.generate.return_value = json.dumps({
        "epic_number": 2,
        "title": "LLM-Powered Content Extraction",
        "goal": "Implement OLLAMA-based extraction of structured information from BMAD markdown.",
        "status": "dev",
        "related_stories": None  # Will be extracted from markdown links
    })

    result = await extraction_service.extract_epic(sample_epic_document)

    assert isinstance(result, ExtractedEpicSchema)
    assert result.epic_number == 2
    assert result.title == "LLM-Powered Content Extraction"
    assert result.goal == "Implement OLLAMA-based extraction of structured information from BMAD markdown."
    assert result.status == "dev"
    assert len(result.related_stories) == 3  # Extracted from markdown links
    assert "stories/story-2-1.md" in result.related_stories
    assert "stories/story-2-2.md" in result.related_stories
    assert "docs/stories/story-2-3.md" in result.related_stories
    assert result.confidence_score == 1.0  # All 4 fields present


@pytest.mark.asyncio
async def test_extract_epic_partial_data(extraction_service, mock_ollama_service):
    """Test extraction with missing fields (partial data)."""
    doc = Mock(spec=Document)
    doc.id = "epic-partial"
    doc.content = """# Epic 3: Partial Epic

Status: Draft

No goal section.
"""

    # Mock OLLAMA response with missing goal
    mock_ollama_service.generate.return_value = json.dumps({
        "epic_number": 3,
        "title": "Partial Epic",
        "goal": None,
        "status": "draft",
        "related_stories": None
    })

    result = await extraction_service.extract_epic(doc)

    assert result.epic_number == 3
    assert result.title == "Partial Epic"
    assert result.goal is None
    assert result.status == "draft"
    assert result.related_stories == [] or result.related_stories is None
    assert result.confidence_score < 1.0  # Missing fields


@pytest.mark.asyncio
async def test_extract_epic_llm_error(extraction_service, mock_ollama_service):
    """Test extraction failure handling (LLM error)."""
    doc = Mock(spec=Document)
    doc.id = "epic-error"
    doc.content = "Some content"

    # Mock OLLAMA to raise exception
    mock_ollama_service.generate.side_effect = Exception("OLLAMA timeout")

    result = await extraction_service.extract_epic(doc)

    assert isinstance(result, ExtractedEpicSchema)
    assert result.title == "Extraction Failed"
    assert result.confidence_score == 0.0


@pytest.mark.asyncio
async def test_extract_epic_json_parse_failure_with_regex_fallback(extraction_service, mock_ollama_service):
    """Test JSON parse failure triggers regex fallback."""
    doc = Mock(spec=Document)
    doc.id = "epic-json-fail"
    doc.content = """# Epic 5: Test Epic

**Status:** Done

## Epic Goal

Test the regex fallback.
"""

    # Mock OLLAMA to return invalid JSON
    mock_ollama_service.generate.return_value = "NOT JSON AT ALL"

    result = await extraction_service.extract_epic(doc)

    # Regex fallback should extract basic fields
    assert result.epic_number == 5
    assert result.title == "Test Epic"
    assert result.status == "done"
    assert "Test the regex fallback" in (result.goal or "")
    assert result.confidence_score > 0.0  # Some fields extracted


@pytest.mark.asyncio
async def test_extract_story_links_various_formats():
    """Test markdown link parsing with various formats."""
    service = EpicExtractionService()

    content = """
# Epic Test

Stories:
- [Story 1.1](stories/story-1-1.md)
- [Story 1.2](docs/stories/story-1-2.md)
- [Story 1.3](/docs/stories/story-1-3.md)
- [Not a story](some-other-doc.md)
- [External](https://example.com)
"""

    links = service._extract_story_links(content)

    assert len(links) == 3
    assert "stories/story-1-1.md" in links
    assert "docs/stories/story-1-2.md" in links
    assert "docs/stories/story-1-3.md" in links  # Leading / stripped
    assert "some-other-doc.md" not in links  # Filtered out


@pytest.mark.asyncio
async def test_ollama_called_with_json_format(extraction_service, mock_ollama_service, sample_epic_document):
    """Test that OLLAMA is called with format_json=True."""
    mock_ollama_service.generate.return_value = json.dumps({
        "epic_number": 2,
        "title": "Test",
        "goal": None,
        "status": None,
        "related_stories": None
    })

    await extraction_service.extract_epic(sample_epic_document)

    mock_ollama_service.generate.assert_called_once()
    call_kwargs = mock_ollama_service.generate.call_args.kwargs
    assert call_kwargs["format_json"] is True


@pytest.mark.asyncio
async def test_confidence_score_calculation():
    """Test confidence score calculation logic."""
    service = EpicExtractionService()

    # All 4 fields: 1.0
    assert service._calculate_confidence({
        "title": "Test",
        "goal": "Goal text",
        "status": "dev",
        "related_stories": ["story.md"]
    }) == 1.0

    # 3 fields: 0.75
    assert service._calculate_confidence({
        "title": "Test",
        "goal": "Goal text",
        "status": "dev",
        "related_stories": None
    }) == 0.75

    # 2 fields: 0.5
    assert service._calculate_confidence({
        "title": "Test",
        "goal": None,
        "status": "dev",
        "related_stories": None
    }) == 0.5

    # 1 field (title only): 0.25
    assert service._calculate_confidence({
        "title": "Test",
        "goal": None,
        "status": None,
        "related_stories": None
    }) == 0.25

    # Empty arrays count as not populated
    assert service._calculate_confidence({
        "title": "Test",
        "goal": "",
        "status": None,
        "related_stories": []
    }) == 0.25


@pytest.mark.asyncio
async def test_empty_related_stories_handled(extraction_service, mock_ollama_service):
    """Test that empty related_stories array is handled correctly in confidence scoring."""
    doc = Mock(spec=Document)
    doc.id = "epic-no-stories"
    doc.content = "# Epic 1: No Stories"

    mock_ollama_service.generate.return_value = json.dumps({
        "epic_number": 1,
        "title": "No Stories",
        "goal": "Some goal",
        "status": "draft",
        "related_stories": []
    })

    result = await extraction_service.extract_epic(doc)

    # Empty array should reduce confidence
    assert result.confidence_score < 1.0


# Story 2.4: Status Detection Enhancement Tests for Epics


@pytest.mark.asyncio
async def test_epic_status_bold_format(extraction_service):
    """Test epic status detection with bold format: **Status:** Draft."""
    doc = Mock(spec=Document)
    doc.id = "epic-bold"
    doc.content = """
# Epic 1: Test Epic

**Status:** Draft

## Epic Goal

Test epic goal
"""

    from unittest.mock import patch
    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_epic(doc)
        assert result.status == "draft"


@pytest.mark.asyncio
async def test_epic_status_bracketed_format(extraction_service):
    """Test epic status detection with bracketed format."""
    doc = Mock(spec=Document)
    doc.id = "epic-bracketed"
    doc.content = """
# Epic 2: Test Epic

[Status: Done]

## Epic Goal

Test epic goal
"""

    from unittest.mock import patch
    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_epic(doc)
        assert result.status == "done"


@pytest.mark.asyncio
async def test_epic_status_html_comment(extraction_service):
    """Test epic status detection with HTML comment."""
    doc = Mock(spec=Document)
    doc.id = "epic-html"
    doc.content = """
# Epic 3: Test Epic

<!-- status: dev -->

## Epic Goal

Test epic goal
"""

    from unittest.mock import patch
    with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
        result = await extraction_service.extract_epic(doc)
        assert result.status == "dev"


@pytest.mark.asyncio
async def test_epic_status_case_insensitive(extraction_service):
    """Test that epic status detection is case-insensitive."""
    test_cases = [
        ("**STATUS:** DRAFT", "draft"),
        ("Status: DEV", "dev"),
        ("[Status: DONE]", "done"),
    ]

    for content_status, expected in test_cases:
        doc = Mock(spec=Document)
        doc.id = f"epic-case-{expected}"
        doc.content = f"""
# Epic: Test

{content_status}

## Epic Goal
Test goal
"""

        from unittest.mock import patch
        with patch.object(json, 'loads', side_effect=json.JSONDecodeError("test", "", 0)):
            result = await extraction_service.extract_epic(doc)
            assert result.status == expected
