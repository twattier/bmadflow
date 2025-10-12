"""Unit tests for markdown parser utility."""

from app.utils.markdown_parser import (
    HeaderInfo,
    extract_headers,
    find_nearest_header,
    header_to_anchor,
)


class TestHeaderToAnchor:
    """Tests for header_to_anchor function."""

    def test_header_to_anchor_basic(self):
        """Test basic header conversion."""
        assert header_to_anchor("Database Schema") == "database-schema"
        assert header_to_anchor("Introduction") == "introduction"
        assert header_to_anchor("API Endpoints") == "api-endpoints"

    def test_header_to_anchor_special_chars(self):
        """Test header with special characters."""
        assert header_to_anchor("API (v2.0)") == "api-v20"
        assert header_to_anchor("Introduction & Overview") == "introduction--overview"
        assert header_to_anchor("Section #1: Getting Started") == "section-1-getting-started"
        assert header_to_anchor("User's Guide") == "users-guide"
        assert header_to_anchor("What/Why/How?") == "whatwhyhow"

    def test_header_to_anchor_edge_cases(self):
        """Test edge cases: empty, all special chars, whitespace."""
        assert header_to_anchor("") == ""
        assert header_to_anchor("@#$%^&*()") == ""
        assert header_to_anchor("   ") == ""
        assert header_to_anchor("   Spaces   ") == "spaces"

    def test_header_to_anchor_numbers(self):
        """Test headers with numbers."""
        assert header_to_anchor("Chapter 1") == "chapter-1"
        assert header_to_anchor("2024 Roadmap") == "2024-roadmap"
        assert header_to_anchor("v2.0.1 Release") == "v201-release"

    def test_header_to_anchor_multiple_spaces(self):
        """Test headers with multiple consecutive spaces."""
        assert header_to_anchor("Multiple   Spaces   Here") == "multiple---spaces---here"

    def test_header_to_anchor_mixed_case(self):
        """Test case conversion."""
        assert header_to_anchor("MixedCase") == "mixedcase"
        assert header_to_anchor("UPPERCASE") == "uppercase"
        assert header_to_anchor("camelCase") == "camelcase"


class TestExtractHeaders:
    """Tests for extract_headers function."""

    def test_extract_headers_simple(self):
        """Test extraction of simple H1, H2, H3 headers."""
        content = """# Title
Some text
## Section 1
More text
### Subsection
Final text
"""
        headers = extract_headers(content)

        assert len(headers) == 3
        assert headers[0].text == "Title"
        assert headers[0].level == 1
        assert headers[0].anchor == "title"
        assert headers[0].line_number == 0

        assert headers[1].text == "Section 1"
        assert headers[1].level == 2
        assert headers[1].anchor == "section-1"

        assert headers[2].text == "Subsection"
        assert headers[2].level == 3
        assert headers[2].anchor == "subsection"

    def test_extract_headers_nested(self):
        """Test multiple headers at different levels."""
        content = """# Main Title
Content
## Section A
### Subsection A1
### Subsection A2
## Section B
### Subsection B1
"""
        headers = extract_headers(content)

        assert len(headers) == 6
        assert [h.level for h in headers] == [1, 2, 3, 3, 2, 3]
        assert headers[0].text == "Main Title"
        assert headers[1].text == "Section A"
        assert headers[2].text == "Subsection A1"
        assert headers[3].text == "Subsection A2"
        assert headers[4].text == "Section B"
        assert headers[5].text == "Subsection B1"

    def test_extract_headers_ignore_h4_h5_h6(self):
        """Test that H4-H6 headers are ignored."""
        content = """# H1 Header
## H2 Header
### H3 Header
#### H4 Header (ignored)
##### H5 Header (ignored)
###### H6 Header (ignored)
"""
        headers = extract_headers(content)

        assert len(headers) == 3
        assert all(h.level <= 3 for h in headers)
        assert headers[0].text == "H1 Header"
        assert headers[1].text == "H2 Header"
        assert headers[2].text == "H3 Header"

    def test_extract_headers_with_special_chars(self):
        """Test headers containing special characters."""
        content = """# Introduction & Overview
## API (v2.0)
### User's Guide
"""
        headers = extract_headers(content)

        assert len(headers) == 3
        assert headers[0].anchor == "introduction--overview"
        assert headers[1].anchor == "api-v20"
        assert headers[2].anchor == "users-guide"

    def test_extract_headers_empty_content(self):
        """Test extraction from empty content."""
        assert extract_headers("") == []
        assert extract_headers("   ") == []
        assert extract_headers("\n\n\n") == []

    def test_extract_headers_no_headers(self):
        """Test content without headers."""
        content = """This is just plain text.
No headers here.
Just paragraphs.
"""
        assert extract_headers(content) == []

    def test_extract_headers_char_positions(self):
        """Test that character positions are calculated correctly."""
        content = "# Title\nSome text\n## Section\n"
        headers = extract_headers(content)

        assert len(headers) == 2
        assert headers[0].char_position == 0  # Start of document
        assert headers[1].char_position == 18  # After "# Title\nSome text\n"

    def test_extract_headers_inline_hashes(self):
        """Test that inline # symbols are not treated as headers."""
        content = """# Real Header
This is #not a header
Neither is this # one
## Another Real Header
"""
        headers = extract_headers(content)

        assert len(headers) == 2
        assert headers[0].text == "Real Header"
        assert headers[1].text == "Another Real Header"

    def test_extract_headers_whitespace_handling(self):
        """Test headers with extra whitespace."""
        content = """#   Title with spaces
##  Section
###   Subsection
"""
        headers = extract_headers(content)

        assert len(headers) == 3
        assert headers[0].text == "Title with spaces"
        assert headers[1].text == "Section"
        assert headers[2].text == "Subsection"


class TestFindNearestHeader:
    """Tests for find_nearest_header function."""

    def test_find_nearest_header_single(self):
        """Test finding header with single preceding header."""
        headers = [
            HeaderInfo("Title", 1, 0, "title", 0),
            HeaderInfo("Section", 2, 5, "section", 100),
        ]

        # Chunk at position 150 should find "section"
        assert find_nearest_header(150, headers) == "section"

        # Chunk at position 50 should find "title"
        assert find_nearest_header(50, headers) == "title"

    def test_find_nearest_header_multiple(self):
        """Test chunk with multiple preceding headers picks nearest."""
        headers = [
            HeaderInfo("Title", 1, 0, "title", 0),
            HeaderInfo("Section A", 2, 5, "section-a", 50),
            HeaderInfo("Section B", 2, 10, "section-b", 100),
            HeaderInfo("Section C", 2, 15, "section-c", 150),
        ]

        # Chunk at 175 should find "section-c" (nearest)
        assert find_nearest_header(175, headers) == "section-c"

        # Chunk at 125 should find "section-b"
        assert find_nearest_header(125, headers) == "section-b"

        # Chunk at 75 should find "section-a"
        assert find_nearest_header(75, headers) == "section-a"

    def test_find_nearest_header_none_before_first(self):
        """Test chunk before first header returns None."""
        headers = [
            HeaderInfo("Title", 1, 5, "title", 100),
            HeaderInfo("Section", 2, 10, "section", 200),
        ]

        # Chunk at position 50 is before first header
        assert find_nearest_header(50, headers) is None

        # Chunk at position 0 is before first header
        assert find_nearest_header(0, headers) is None

    def test_find_nearest_header_empty_list(self):
        """Test with empty headers list."""
        assert find_nearest_header(100, []) is None

    def test_find_nearest_header_exact_position(self):
        """Test chunk at exact header position."""
        headers = [
            HeaderInfo("Title", 1, 0, "title", 0),
            HeaderInfo("Section", 2, 5, "section", 100),
        ]

        # Chunk at exactly position 100 (header position)
        # Should NOT find the header at 100, only preceding ones
        assert find_nearest_header(100, headers) == "title"

        # Chunk at position 101 (after header)
        assert find_nearest_header(101, headers) == "section"

    def test_find_nearest_header_same_position_prefers_highest_level(self):
        """Test multiple headers at same position prefers H1 over H2 over H3."""
        headers = [
            HeaderInfo("Title H1", 1, 0, "title-h1", 50),
            HeaderInfo("Title H2", 2, 0, "title-h2", 50),
            HeaderInfo("Title H3", 3, 0, "title-h3", 50),
        ]

        # Should prefer H1 (level 1) over others
        assert find_nearest_header(100, headers) == "title-h1"

    def test_find_nearest_header_empty_anchor(self):
        """Test header with empty anchor (all special chars)."""
        headers = [
            HeaderInfo("@#$%", 1, 0, "", 0),  # Empty anchor
            HeaderInfo("Section", 2, 5, "section", 100),
        ]

        # Should return None for empty anchor
        assert find_nearest_header(50, headers) is None

        # Later position should find valid anchor
        assert find_nearest_header(150, headers) == "section"

    def test_find_nearest_header_real_document_scenario(self):
        """Test realistic document with multiple sections."""
        # Simulate a real markdown document structure
        headers = [
            HeaderInfo("Introduction", 1, 0, "introduction", 0),
            HeaderInfo("Background", 2, 10, "background", 150),
            HeaderInfo("Motivation", 3, 15, "motivation", 200),
            HeaderInfo("Architecture", 2, 25, "architecture", 350),
            HeaderInfo("Database Schema", 3, 30, "database-schema", 450),
            HeaderInfo("API Design", 2, 45, "api-design", 650),
        ]

        # Chunk in Introduction section
        assert find_nearest_header(100, headers) == "introduction"

        # Chunk in Background section
        assert find_nearest_header(175, headers) == "background"

        # Chunk in Motivation subsection
        assert find_nearest_header(300, headers) == "motivation"

        # Chunk in Database Schema subsection
        assert find_nearest_header(500, headers) == "database-schema"

        # Chunk in API Design section
        assert find_nearest_header(700, headers) == "api-design"
