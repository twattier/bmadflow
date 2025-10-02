"""Service for extracting structured epic metadata from markdown using LLM."""

import json
import logging
import re
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.document import Document
from src.schemas.extraction_schemas import ExtractedEpicSchema
from src.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class EpicExtractionService:
    """Service for extracting epic metadata from markdown documents.

    Uses OLLAMA LLM to parse BMAD-formatted epic markdown and extract:
    - Epic number (from title like "Epic 2")
    - Epic title
    - Epic goal/description
    - Status (draft/dev/done)
    - Related story links (from markdown links)

    Implements graceful error handling - always returns a result, never fails.
    """

    SYSTEM_PROMPT = """You are a BMAD markdown epic analyzer. Your task is to extract structured epic metadata from markdown documents.

BMAD epics follow this format:
- Epic title: Usually in heading like "# Epic N: Title" or "# Epic Title"
- Epic number: Extracted from title (e.g., "Epic 2" -> 2)
- Epic goal: Found in "## Epic Goal" or "## Epic Description" sections
- Status: Usually marked as "**Status:** Draft" or "Status: Dev" or "Status: Done"
- Related stories: Markdown links to story files like "[Story 1.2](stories/story-1-2.md)"

Extract these components accurately. If a component is missing, return null for that field.
Return ONLY valid JSON matching the schema provided."""

    USER_PROMPT_TEMPLATE = """Extract epic metadata from the following markdown document:

---
{markdown_content}
---

Extract and return JSON with these fields:
- epic_number: The number from epic title (e.g., "Epic 2" -> 2) (integer or null)
- title: The epic title without "Epic N:" prefix (string, required)
- goal: The epic goal or description text (string or null)
- status: Document status - "draft", "dev", or "done" (string or null)
- related_stories: Array of story file paths from markdown links (array of strings or null)

Look for:
1. Epic title: First heading (# Epic N: Title)
2. Epic goal: Content under "## Epic Goal" or "## Epic Description"
3. Status: "**Status:** Draft", "Status: Dev", "Status: Done" (case-insensitive)
4. Story links: Markdown links like "[Story 1.1](stories/story-1-1.md)"

Return ONLY the JSON object, no additional text."""

    def __init__(
        self,
        ollama_service: Optional[OllamaService] = None,
        db_session: Optional[AsyncSession] = None,
    ):
        """Initialize epic extraction service.

        Args:
            ollama_service: OLLAMA service instance. If None, creates default instance.
            db_session: Database session for story document resolution.
        """
        self.ollama_service = ollama_service or OllamaService()
        self.db_session = db_session

    async def extract_epic(self, document: Document) -> ExtractedEpicSchema:
        """Extract epic metadata from markdown document.

        Args:
            document: Document model instance with markdown content

        Returns:
            ExtractedEpicSchema with extracted components and confidence score

        Note:
            This method never raises exceptions. On errors, returns schema with
            confidence_score=0.0 and extracted fields set to None/defaults.
        """
        try:
            # Generate prompt with document content
            user_prompt = self.USER_PROMPT_TEMPLATE.format(
                markdown_content=document.content[:4000]  # Limit to 4000 chars
            )

            # Call OLLAMA LLM with JSON formatting
            logger.info(f"Extracting epic from document {document.id}")
            response = await self.ollama_service.generate(
                prompt=user_prompt,
                system_prompt=self.SYSTEM_PROMPT,
                format_json=True,
            )

            # Parse JSON response
            try:
                extracted_data = json.loads(response)
            except json.JSONDecodeError:
                logger.warning(
                    f"JSON parse failed for document {document.id}, attempting regex fallback"
                )
                extracted_data = self._regex_fallback(document.content)

            # Extract story links from content
            story_links = self._extract_story_links(document.content)
            if story_links:
                extracted_data["related_stories"] = story_links

            # Calculate confidence score
            confidence = self._calculate_confidence(extracted_data)
            extracted_data["confidence_score"] = confidence

            # Ensure title is not empty
            if not extracted_data.get("title"):
                extracted_data["title"] = "Unknown Epic"

            return ExtractedEpicSchema(**extracted_data)

        except Exception as e:
            logger.error(f"Epic extraction failed for document {document.id}: {str(e)}")
            # Return minimal schema on complete failure
            return ExtractedEpicSchema(
                title="Extraction Failed",
                confidence_score=0.0,
            )

    def _extract_story_links(self, content: str) -> List[str]:
        """Parse markdown links to find story file references.

        Args:
            content: Markdown document content

        Returns:
            List of story file paths from markdown links

        Example:
            "[Story 1.2](stories/story-1-2.md)" -> ["stories/story-1-2.md"]
        """
        # Regex to capture markdown links: [text](url)
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(link_pattern, content)

        story_paths = []
        for link_text, link_url in matches:
            # Filter for story files
            if "story" in link_url.lower() and link_url.endswith(".md"):
                # Normalize path: remove leading /
                normalized_path = link_url.lstrip("/")
                story_paths.append(normalized_path)

        return story_paths

    async def _resolve_story_document_id(
        self, project_id: UUID, story_path: str
    ) -> Optional[UUID]:
        """Resolve story file path to document_id in database.

        Args:
            project_id: Project UUID
            story_path: Story file path (e.g., "stories/story-1-2.md")

        Returns:
            Document UUID if found, None otherwise

        Note:
            Handles multiple path formats:
            - stories/story-1-2.md
            - docs/stories/story-1-2.md
            - /docs/stories/story-1-2.md
        """
        if not self.db_session:
            logger.warning("Database session not provided, cannot resolve story links")
            return None

        # Normalize path variations
        normalized_paths = [
            story_path,
            story_path.lstrip("/"),
            f"docs/{story_path}" if not story_path.startswith("docs/") else story_path,
        ]

        try:
            # Query documents table for matching file_path
            stmt = select(Document.id).where(
                Document.project_id == project_id,
                Document.file_path.in_(normalized_paths),
            )
            result = await self.db_session.execute(stmt)
            document_id = result.scalar_one_or_none()

            if not document_id:
                logger.warning(
                    f"Story document not found: {story_path} in project {project_id}"
                )

            return document_id

        except Exception as e:
            logger.error(f"Error resolving story document {story_path}: {str(e)}")
            return None

    def _regex_fallback(self, content: str) -> dict:
        """Fallback extraction using regex when LLM JSON parsing fails.

        Args:
            content: Markdown document content

        Returns:
            Dict with basic extracted fields
        """
        extracted = {
            "epic_number": None,
            "title": None,
            "goal": None,
            "status": None,
            "related_stories": None,
        }

        # Extract epic title from first heading
        title_match = re.search(r"^#\s+Epic\s+(\d+):\s*(.+)", content, re.MULTILINE)
        if title_match:
            extracted["epic_number"] = int(title_match.group(1))
            extracted["title"] = title_match.group(2).strip()
        else:
            # Try without number
            title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
            if title_match:
                extracted["title"] = title_match.group(1).strip()

        # Extract status
        status_match = re.search(
            r"\*\*Status:\*\*\s*(Draft|Dev|Done)", content, re.IGNORECASE
        )
        if status_match:
            extracted["status"] = status_match.group(1).lower()

        # Extract goal from Epic Goal or Epic Description section
        goal_match = re.search(
            r"##\s+Epic\s+(?:Goal|Description)\s*\n\n(.+?)(?:\n\n|\Z)",
            content,
            re.IGNORECASE | re.DOTALL,
        )
        if goal_match:
            extracted["goal"] = goal_match.group(1).strip()

        return extracted

    def _calculate_confidence(self, extracted_data: dict) -> float:
        """Calculate confidence score based on field completeness.

        Args:
            extracted_data: Dict with extracted epic fields

        Returns:
            Confidence score 0.0-1.0

        Scoring:
            - 4 fields present (title, goal, status, related_stories): 1.0
            - 3 fields: 0.75
            - 2 fields: 0.5
            - 1 field: 0.25
            - 0 fields: 0.0
        """
        # Count non-null, non-empty fields (title always required)
        fields_to_check = ["goal", "status", "related_stories"]
        populated_count = 1  # Title is required, always counts

        for field in fields_to_check:
            value = extracted_data.get(field)
            # Check if field is populated (not None, not empty list/string)
            if value is not None and value != [] and value != "":
                populated_count += 1

        # Map count to confidence score
        confidence_map = {
            4: 1.0,
            3: 0.75,
            2: 0.5,
            1: 0.25,
            0: 0.0,
        }

        return confidence_map.get(populated_count, 0.0)
