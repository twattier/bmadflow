"""Integration tests for header anchor extraction in document processing pipeline.

Tests the end-to-end flow from markdown processing through embedding storage,
verifying that header anchors are correctly extracted and persisted.
"""

from pathlib import Path

import pytest

from app.services.docling_service import DoclingService


@pytest.fixture
def docling_service():
    """Create DoclingService for integration testing."""
    return DoclingService()


@pytest.fixture
def sample_prd_content():
    """Load sample PRD markdown content for testing.

    Uses a realistic PRD structure with multiple sections and headers.
    """
    return """# Product Requirements Document

## 1. Introduction

This document outlines the requirements for BMADFlow, a documentation
management and RAG system.

### 1.1 Purpose

The purpose of this system is to provide AI-powered documentation search
and question answering capabilities.

### 1.2 Scope

The system will support markdown, CSV, YAML, and JSON file formats.

## 2. Features

The following features are included in the MVP release.

### 2.1 Document Sync

Automatically sync documentation from GitHub repositories.

### 2.2 Vector Search

Perform semantic search across all documentation using embeddings.

### 2.3 RAG Chat

Interactive chat interface with context-aware responses.

## 3. Architecture

This section describes the high-level architecture.

### 3.1 Backend

FastAPI-based REST API with PostgreSQL database.

### 3.2 Frontend

React TypeScript application with shadcn/ui components.

## 4. Database Schema

The database includes the following tables.

### 4.1 Projects

Store project metadata and GitHub URLs.

### 4.2 Documents

Track synced documentation files.

### 4.3 Chunks

Store text chunks with vector embeddings.

## 5. API Endpoints

REST API endpoints for all operations.

### 5.1 Project Management

CRUD operations for projects.

### 5.2 Document Operations

Sync and retrieve documents.

### 5.3 Search

Vector similarity search endpoint.
"""


@pytest.mark.asyncio
async def test_process_prd_with_headers(docling_service, sample_prd_content):
    """Integration test: Process PRD with multiple sections and verify anchor extraction.

    Tests that header anchors are correctly extracted for a realistic PRD document
    with nested sections (H1, H2, H3).
    """
    # Process the PRD content
    chunks = await docling_service.process_markdown(sample_prd_content)

    # Verify chunks were generated
    assert len(chunks) > 0, "Should generate chunks from PRD content"

    # Verify header anchors are populated for chunks under headers
    anchored_chunks = [c for c in chunks if c.header_anchor is not None]
    assert len(anchored_chunks) > 0, "Should have chunks with header anchors"

    # Verify at least 5+ unique header anchors extracted
    unique_anchors = set(c.header_anchor for c in chunks if c.header_anchor)
    assert (
        len(unique_anchors) >= 5
    ), f"Should extract at least 5 unique headers, got {len(unique_anchors)}: {unique_anchors}"

    # Verify expected anchors are present (sampling)
    expected_anchors = {
        "product-requirements-document",
        "1-introduction",
        "11-purpose",
        "2-features",
        "21-document-sync",
        "3-architecture",
        "31-backend",
        "4-database-schema",
        "41-projects",
        "5-api-endpoints",
    }

    found_anchors = unique_anchors & expected_anchors
    assert len(found_anchors) >= 3, f"Should find at least 3 expected anchors, got: {found_anchors}"

    # Print sample chunks for manual verification
    print("\n=== Sample Chunks with Anchors ===")
    for i, chunk in enumerate(chunks[:10]):  # First 10 chunks
        print(f"Chunk {i}: anchor={chunk.header_anchor}, text={chunk.text[:60].strip()}...")


@pytest.mark.asyncio
async def test_first_chunk_before_header_has_no_anchor(docling_service):
    """Test that content before the first header has anchor=None."""
    markdown_content = """This is preamble content before any headers.

It might include copyright info or other metadata.

# First Section

Now we have content under a header.

## Subsection

More content here.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    assert len(chunks) > 0

    # Check that at least one chunk has None anchor (content before first header)
    chunks_without_anchor = [c for c in chunks if c.header_anchor is None]
    assert len(chunks_without_anchor) > 0, "Should have chunks without anchor (before first header)"

    # Check that some chunks have anchors (under headers)
    chunks_with_anchor = [c for c in chunks if c.header_anchor is not None]
    assert len(chunks_with_anchor) > 0, "Should have chunks with anchors (under headers)"


@pytest.mark.asyncio
async def test_header_anchor_format_validation(docling_service, sample_prd_content):
    """Verify all extracted header anchors follow correct format (lowercase, hyphenated)."""
    chunks = await docling_service.process_markdown(sample_prd_content)

    anchored_chunks = [c for c in chunks if c.header_anchor is not None]
    assert len(anchored_chunks) > 0, "Need chunks with anchors to test format"

    for chunk in anchored_chunks:
        anchor = chunk.header_anchor
        # Should be lowercase
        assert anchor == anchor.lower(), f"Anchor should be lowercase: {anchor}"
        # Should not contain spaces
        assert " " not in anchor, f"Anchor should not contain spaces: {anchor}"
        # Should not contain special characters
        assert (
            "(" not in anchor and ")" not in anchor
        ), f"Anchor should not contain parens: {anchor}"
        assert "&" not in anchor, f"Anchor should not contain ampersand: {anchor}"


@pytest.mark.asyncio
async def test_nested_headers_hierarchy(docling_service):
    """Test that nested headers (H1 > H2 > H3) produce correct anchors."""
    markdown_content = """# Top Level

Content at top level.

## Second Level

Content at second level.

### Third Level

Content at third level.

### Another Third Level

More third level content.

## Back to Second Level

Back to H2.
"""

    chunks = await docling_service.process_markdown(markdown_content)

    # Extract unique anchors
    unique_anchors = set(c.header_anchor for c in chunks if c.header_anchor)

    # Should have anchors for each header level
    expected_anchors = {
        "top-level",
        "second-level",
        "third-level",
        "another-third-level",
        "back-to-second-level",
    }

    found = unique_anchors & expected_anchors
    assert len(found) >= 3, f"Should find at least 3 of the expected anchors, got: {found}"


@pytest.mark.asyncio
async def test_real_bmad_documentation(docling_service):
    """Test with actual BMAD project documentation if available.

    This test attempts to load real documentation from the project's docs/ folder.
    If not available, the test is skipped.
    """
    # Try to load actual BMAD documentation
    docs_path = Path("/home/wsluser/dev/bmad-test/bmadflow/docs")

    if not docs_path.exists():
        pytest.skip("BMAD docs directory not found")

    # Try to read PRD or architecture doc
    prd_file = docs_path / "prd.md"
    if not prd_file.exists():
        prd_file = docs_path / "architecture" / "database-schema.md"

    if not prd_file.exists():
        pytest.skip("No suitable documentation file found for testing")

    # Read the file
    with open(prd_file, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        pytest.skip("Documentation file is empty")

    # Process the real documentation
    chunks = await docling_service.process_markdown(content)

    # Verify processing succeeded
    assert len(chunks) > 0, f"Should generate chunks from {prd_file.name}"

    # Verify header anchors extracted
    anchored_chunks = [c for c in chunks if c.header_anchor is not None]
    assert len(anchored_chunks) > 0, f"Should extract header anchors from {prd_file.name}"

    unique_anchors = set(c.header_anchor for c in chunks if c.header_anchor)
    assert len(unique_anchors) >= 3, f"Should have at least 3 unique anchors from {prd_file.name}"

    # Print summary
    print(f"\n=== Real Documentation Test: {prd_file.name} ===")
    print(f"Generated {len(chunks)} chunks")
    print(f"Extracted {len(unique_anchors)} unique header anchors:")
    for anchor in sorted(unique_anchors)[:10]:  # Show first 10
        print(f"  - {anchor}")
