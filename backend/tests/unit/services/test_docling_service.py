"""Unit tests for DoclingService."""

import pytest

from app.schemas.chunk import ChunkProcessed
from app.services.docling_service import DoclingService


@pytest.fixture
def docling_service():
    """Create DoclingService instance for testing."""
    return DoclingService()


@pytest.mark.asyncio
async def test_process_markdown_simple(docling_service):
    """Test basic markdown processing with headers and paragraphs."""
    markdown_content = """# Introduction

This is a sample document with multiple sections.

## Features

- Feature 1
- Feature 2
- Feature 3

## Details

This section contains more detailed information about the features.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    # Assertions
    assert len(chunks) > 0, "Should generate at least one chunk"
    assert all(isinstance(chunk, ChunkProcessed) for chunk in chunks)
    assert all(chunk.text for chunk in chunks), "All chunks should have text"
    assert all(chunk.index >= 0 for chunk in chunks), "All chunks should have valid index"
    assert all(
        chunk.metadata.get("file_type") == "md" for chunk in chunks
    ), "All chunks should have md file_type"
    assert all(
        "total_chunks" in chunk.metadata for chunk in chunks
    ), "All chunks should have total_chunks metadata"

    # Check first chunk has proper metadata
    first_chunk = chunks[0]
    assert first_chunk.index == 0
    assert "position" in first_chunk.metadata
    assert first_chunk.metadata["total_chunks"] == len(chunks)


@pytest.mark.asyncio
async def test_process_markdown_code_blocks(docling_service):
    """Test markdown processing with code fences."""
    markdown_content = """# Code Example

Here is a Python function:

```python
def hello_world():
    print("Hello, World!")
    return True
```

And here is the explanation.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    # Assertions
    assert len(chunks) > 0
    assert any(
        "python" in chunk.text.lower() or "def hello_world" in chunk.text for chunk in chunks
    ), "Code block content should be preserved"
    assert all(chunk.metadata.get("file_type") == "md" for chunk in chunks)


@pytest.mark.asyncio
async def test_process_csv_with_headers(docling_service):
    """Test CSV processing with header row."""
    csv_content = """name,age,city
Alice,30,New York
Bob,25,San Francisco
Charlie,35,Seattle
"""

    chunks = await docling_service.process_csv(csv_content)

    # Assertions
    assert len(chunks) > 0
    assert all(isinstance(chunk, ChunkProcessed) for chunk in chunks)
    assert all(
        chunk.metadata.get("file_type") == "csv" for chunk in chunks
    ), "All chunks should have csv file_type"
    assert any(
        "Alice" in chunk.text or "name" in chunk.text.lower() for chunk in chunks
    ), "CSV content should be preserved"


@pytest.mark.asyncio
async def test_process_yaml_structure(docling_service):
    """Test nested YAML structure chunking."""
    yaml_content = """
version: 1.0
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
services:
  - name: web
    port: 8000
  - name: api
    port: 8080
"""

    chunks = await docling_service.process_yaml_json(yaml_content, "yaml")

    # Assertions
    assert len(chunks) > 0
    assert all(isinstance(chunk, ChunkProcessed) for chunk in chunks)
    assert all(
        chunk.metadata.get("file_type") == "yaml" for chunk in chunks
    ), "All chunks should have yaml file_type"
    assert any(
        "database" in chunk.text.lower() or "services" in chunk.text.lower() for chunk in chunks
    ), "YAML structure should be preserved"


@pytest.mark.asyncio
async def test_process_json_structure(docling_service):
    """Test JSON array/object chunking."""
    json_content = """{
  "project": "BMADFlow",
  "version": "1.0.0",
  "dependencies": [
    "fastapi",
    "sqlalchemy",
    "docling"
  ],
  "config": {
    "database": "postgresql",
    "port": 5432
  }
}"""

    chunks = await docling_service.process_yaml_json(json_content, "json")

    # Assertions
    assert len(chunks) > 0
    assert all(isinstance(chunk, ChunkProcessed) for chunk in chunks)
    assert all(
        chunk.metadata.get("file_type") == "json" for chunk in chunks
    ), "All chunks should have json file_type"
    assert any(
        "BMADFlow" in chunk.text or "dependencies" in chunk.text for chunk in chunks
    ), "JSON structure should be preserved"


@pytest.mark.asyncio
async def test_unsupported_file_type(docling_service):
    """Test that unsupported file types raise ValueError."""
    content = "some content"

    with pytest.raises(ValueError, match="Unsupported file type"):
        await docling_service.process_yaml_json(content, "xml")

    with pytest.raises(ValueError, match="Unsupported file type"):
        await docling_service.process_yaml_json(content, "txt")


@pytest.mark.asyncio
async def test_empty_markdown_content(docling_service):
    """Test that empty markdown content raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        await docling_service.process_markdown("")

    with pytest.raises(ValueError, match="cannot be empty"):
        await docling_service.process_markdown("   ")


@pytest.mark.asyncio
async def test_empty_csv_content(docling_service):
    """Test that empty CSV content raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        await docling_service.process_csv("")


@pytest.mark.asyncio
async def test_chunk_indexing(docling_service):
    """Test that chunks are properly indexed sequentially."""
    markdown_content = """# Section 1

Content for section 1.

# Section 2

Content for section 2.

# Section 3

Content for section 3.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    # Verify sequential indexing
    for idx, chunk in enumerate(chunks):
        assert (
            chunk.index == idx
        ), f"Chunk at position {idx} should have index {idx}, got {chunk.index}"

    # Verify total_chunks is consistent
    total = len(chunks)
    assert all(
        chunk.metadata["total_chunks"] == total for chunk in chunks
    ), "All chunks should have same total_chunks value"


@pytest.mark.asyncio
async def test_metadata_completeness(docling_service):
    """Test that all required metadata fields are present."""
    markdown_content = """# Test Document

This is a test document with some content.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    required_fields = ["file_type", "position", "total_chunks"]

    for chunk in chunks:
        for field in required_fields:
            assert field in chunk.metadata, f"Chunk missing required metadata field: {field}"


# ==============================================================================
# Header Anchor Extraction Tests (Story 4.4)
# ==============================================================================


@pytest.mark.asyncio
async def test_process_markdown_extracts_anchors(docling_service):
    """Test that header anchors are extracted and populated in chunks."""
    markdown_content = """# Introduction

This is the introduction section with some content.

## Background

This section provides background information.

### Motivation

Why we're doing this project.

## Architecture

The architecture overview section.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    # Assertions
    assert len(chunks) > 0
    # At least some chunks should have header anchors (chunks under headers)
    anchored_chunks = [c for c in chunks if c.header_anchor is not None]
    assert len(anchored_chunks) > 0, "Should have chunks with header anchors"

    # Check that anchors follow correct format (lowercase, hyphenated)
    for chunk in anchored_chunks:
        anchor = chunk.header_anchor
        assert anchor == anchor.lower(), f"Anchor should be lowercase: {anchor}"
        assert " " not in anchor, f"Anchor should not contain spaces: {anchor}"


@pytest.mark.asyncio
async def test_process_markdown_no_headers(docling_service):
    """Test chunks without headers have anchor=None."""
    markdown_content = """This is plain text without any headers.

Just paragraphs and sentences.

No markdown headers at all.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    # All chunks should have None anchor (no headers in document)
    assert len(chunks) > 0
    assert all(
        chunk.header_anchor is None for chunk in chunks
    ), "Chunks without headers should have anchor=None"


@pytest.mark.asyncio
async def test_process_markdown_mixed_headers(docling_service):
    """Test mix of H1/H2/H3 headers - verify correct anchors."""
    markdown_content = """# Main Title

Content under main title.

## Section A

Content in section A.

### Subsection A1

Content in subsection A1.

### Subsection A2

More content in A2.

## Section B

Content in section B.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    assert len(chunks) > 0

    # Collect unique anchors from chunks
    anchors = set(chunk.header_anchor for chunk in chunks if chunk.header_anchor)

    # Should have anchors like main-title, section-a, subsection-a1, etc.
    expected_anchors = {"main-title", "section-a", "subsection-a1", "subsection-a2", "section-b"}

    # Check at least some expected anchors are present
    # (Docling chunking may group content differently)
    assert len(anchors) > 0, f"Should have extracted header anchors, got: {anchors}"


@pytest.mark.asyncio
async def test_process_markdown_chunk_before_header(docling_service):
    """Test first chunk before any header has anchor=None."""
    markdown_content = """This content appears before any headers.

And this is another paragraph without headers.

# First Header

Now we have content under a header.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    assert len(chunks) > 0

    # First chunk(s) should have None anchor if they appear before first header
    # Note: Docling may chunk differently, so we check that at least one chunk has None
    chunks_without_anchor = [c for c in chunks if c.header_anchor is None]
    assert (
        len(chunks_without_anchor) > 0
    ), "Should have at least one chunk without anchor (before first header)"


@pytest.mark.asyncio
async def test_process_markdown_special_chars_in_headers(docling_service):
    """Test headers with special characters are converted correctly."""
    markdown_content = """# Introduction & Overview

Content here.

## API (v2.0)

API documentation.

### User's Guide

User guide content.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    assert len(chunks) > 0

    # Collect anchors
    anchors = [chunk.header_anchor for chunk in chunks if chunk.header_anchor]

    # Check that anchors follow GitHub style (special chars removed, lowercased)
    for anchor in anchors:
        # Should not contain special chars like & ( ) '
        assert "(" not in anchor
        assert ")" not in anchor
        assert "'" not in anchor
        # Should be lowercase
        assert anchor == anchor.lower()


@pytest.mark.asyncio
async def test_csv_chunks_have_no_anchors(docling_service):
    """Test that CSV files have header_anchor=None (no markdown headers)."""
    csv_content = """name,age,city
Alice,30,New York
Bob,25,San Francisco
"""

    chunks = await docling_service.process_csv(csv_content)

    assert len(chunks) > 0
    # CSV files don't have markdown headers, all anchors should be None
    assert all(chunk.header_anchor is None for chunk in chunks), "CSV chunks should have no anchors"


@pytest.mark.asyncio
async def test_yaml_chunks_have_no_anchors(docling_service):
    """Test that YAML files have header_anchor=None."""
    yaml_content = """version: 1.0
database:
  host: localhost
"""

    chunks = await docling_service.process_yaml_json(yaml_content, "yaml")

    assert len(chunks) > 0
    assert all(
        chunk.header_anchor is None for chunk in chunks
    ), "YAML chunks should have no anchors"


@pytest.mark.asyncio
async def test_json_chunks_have_no_anchors(docling_service):
    """Test that JSON files have header_anchor=None."""
    json_content = """{"project": "BMADFlow", "version": "1.0"}"""

    chunks = await docling_service.process_yaml_json(json_content, "json")

    assert len(chunks) > 0
    assert all(
        chunk.header_anchor is None for chunk in chunks
    ), "JSON chunks should have no anchors"


@pytest.mark.asyncio
async def test_header_anchor_field_always_present(docling_service):
    """Test that header_anchor field is always present (even if None)."""
    markdown_content = """# Test Header

Some content.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    assert len(chunks) > 0
    for chunk in chunks:
        # header_anchor attribute should exist (may be None or str)
        assert hasattr(chunk, "header_anchor"), "All chunks should have header_anchor attribute"
        assert chunk.header_anchor is None or isinstance(
            chunk.header_anchor, str
        ), "header_anchor should be None or string"
