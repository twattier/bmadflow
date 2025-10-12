"""Markdown parser utility for header extraction and anchor generation.

This module provides utilities to extract headers from markdown content and
convert them to anchor format for precise document navigation.
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HeaderInfo:
    """Represents a markdown header with position information.

    Attributes:
        text: The raw header text (without # symbols)
        level: Header level (1 for H1, 2 for H2, 3 for H3)
        line_number: Zero-based line number in the document
        anchor: Pre-computed anchor string in GitHub format
        char_position: Character offset from start of document
    """

    text: str
    level: int
    line_number: int
    anchor: str
    char_position: int


def header_to_anchor(header_text: str) -> str:
    """Convert header text to GitHub-style anchor format.

    Converts markdown header text to lowercase, hyphenated anchor string
    suitable for URL fragments. Follows GitHub's anchor generation rules.

    Args:
        header_text: Raw header text (e.g., "Database Schema")

    Returns:
        Anchor string (e.g., "database-schema"). Returns empty string
        if input is empty or contains only special characters.

    Examples:
        >>> header_to_anchor("Database Schema")
        'database-schema'
        >>> header_to_anchor("API Endpoints (v2.0)")
        'api-endpoints-v20'
        >>> header_to_anchor("Introduction & Overview")
        'introduction--overview'
        >>> header_to_anchor("   Spaces   ")
        'spaces'
        >>> header_to_anchor("@#$%")
        ''
    """
    if not header_text:
        return ""

    # Convert to lowercase
    anchor = header_text.lower()

    # Replace spaces with hyphens
    anchor = anchor.replace(" ", "-")

    # Remove special characters (keep only alphanumeric and hyphens)
    # This regex keeps a-z, 0-9, and hyphens
    anchor = re.sub(r"[^a-z0-9-]", "", anchor)

    # Strip leading/trailing hyphens (cleanup)
    anchor = anchor.strip("-")

    return anchor


def extract_headers(content: str) -> List[HeaderInfo]:
    """Extract H1-H3 headers from markdown content.

    Parses markdown content line-by-line using regex to identify headers
    (H1-H3 only, H4-H6 ignored). Returns header information including text,
    level, position, and pre-computed anchor.

    Args:
        content: Raw markdown document content

    Returns:
        List of HeaderInfo objects, ordered by appearance in document.
        Empty list if no headers found.

    Examples:
        >>> content = '''# Title
        ... Some text
        ... ## Section 1
        ... More text
        ... ### Subsection
        ... '''
        >>> headers = extract_headers(content)
        >>> len(headers)
        3
        >>> headers[0].text
        'Title'
        >>> headers[0].level
        1
        >>> headers[0].anchor
        'title'
    """
    headers = []
    # Pattern matches H1-H3: 1-3 # symbols, followed by space and text
    pattern = r"^(#{1,3})\s+(.+)$"

    char_position = 0
    for line_number, line in enumerate(content.splitlines(keepends=True)):
        # Match on original line (not rstripped) for consistency
        stripped_line = line.rstrip()
        match = re.match(pattern, stripped_line)
        if match:
            level = len(match.group(1))  # Count # symbols
            text = match.group(2).strip()
            anchor = header_to_anchor(text)

            headers.append(
                HeaderInfo(
                    text=text,
                    level=level,
                    line_number=line_number,
                    anchor=anchor,
                    char_position=char_position,
                )
            )

        # Increment by actual line length (including line endings)
        char_position += len(line)

    return headers


def find_nearest_header(chunk_position: int, headers: List[HeaderInfo]) -> Optional[str]:
    """Find the nearest preceding header for a chunk position.

    Identifies the closest H1-H3 header that appears before the given
    chunk position in the document. Used to associate chunks with their
    containing section for navigation.

    Args:
        chunk_position: Character offset of chunk start in document
        headers: List of HeaderInfo objects from extract_headers()

    Returns:
        Anchor string of nearest preceding header, or None if:
        - No headers exist
        - Chunk appears before first header
        - Headers list is empty

    Algorithm:
        - Find all headers with char_position < chunk_position
        - Return anchor of the last (nearest) header
        - If multiple headers at same position, prefer highest level (H1 > H2 > H3)

    Examples:
        >>> headers = [
        ...     HeaderInfo("Title", 1, 0, "title", 0),
        ...     HeaderInfo("Section", 2, 5, "section", 100),
        ... ]
        >>> find_nearest_header(150, headers)
        'section'
        >>> find_nearest_header(50, headers)
        'title'
        >>> find_nearest_header(0, headers)
        None
    """
    if not headers:
        return None

    # Filter headers that appear before chunk position
    preceding_headers = [h for h in headers if h.char_position < chunk_position]

    if not preceding_headers:
        return None

    # If multiple headers at same position, prefer highest level (H1=1 > H2=2 > H3=3)
    # Sort by position DESC (nearest first), then by level ASC (H1 first)
    preceding_headers.sort(key=lambda h: (-h.char_position, h.level))

    # Return anchor of nearest preceding header
    nearest = preceding_headers[0]
    return nearest.anchor if nearest.anchor else None
