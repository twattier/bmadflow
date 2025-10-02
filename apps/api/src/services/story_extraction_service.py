"""Service for extracting structured user story components from markdown using LLM."""

import json
import logging
import re
from typing import Optional

from src.models.document import Document
from src.schemas.extraction_schemas import ExtractedStorySchema
from src.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class StoryExtractionService:
    """Service for extracting user story components from markdown documents.

    Uses OLLAMA LLM to parse BMAD-formatted story markdown and extract:
    - Role ("As a [role]")
    - Action ("I want [action]")
    - Benefit ("So that [benefit]")
    - Acceptance Criteria (numbered list)
    - Status (draft/dev/done)

    Implements graceful error handling - always returns a result, never fails.
    """

    SYSTEM_PROMPT = """You are a BMAD markdown story analyzer. Your task is to extract structured user story components from markdown documents.

BMAD stories follow this format:
- User story: "**As a** [role], **I want** [action], **so that** [benefit]"
- Acceptance Criteria: Numbered list (1., 2., 3., etc.)
- Status: Usually marked as "**Status:** Draft" or "Status: Dev" or "Status: Done"

Extract these components accurately. If a component is missing, return null for that field.
Return ONLY valid JSON matching the schema provided."""

    USER_PROMPT_TEMPLATE = """Extract user story components from the following markdown document:

---
{markdown_content}
---

Extract and return JSON with these fields:
- role: The persona from "As a [role]" (string or null)
- action: The capability from "I want [action]" (string or null)
- benefit: The value from "So that [benefit]" (string or null)
- acceptance_criteria: Array of acceptance criteria items (array of strings or null)
- status: Document status - "draft", "dev", or "done" (string or null)

Look for status in:
1. Explicit markers: "**Status:** Draft", "Status: Dev", "Status: Done" (case-insensitive)
2. If no explicit marker, return null

Return ONLY the JSON object, no additional text."""

    def __init__(self, ollama_service: Optional[OllamaService] = None):
        """Initialize story extraction service.

        Args:
            ollama_service: OLLAMA service instance. If None, creates default instance.
        """
        self.ollama_service = ollama_service or OllamaService()

    async def extract_story(self, document: Document) -> ExtractedStorySchema:
        """Extract user story components from markdown document.

        Args:
            document: Document model instance with markdown content

        Returns:
            ExtractedStorySchema with extracted components and confidence score

        Note:
            This method never raises exceptions. On errors, returns schema with
            confidence_score=0.0 and extracted fields set to None.
        """
        try:
            # Generate prompt with document content
            user_prompt = self.USER_PROMPT_TEMPLATE.format(
                markdown_content=document.content[:4000]  # Limit to 4000 chars for LLM
            )

            # Call OLLAMA with JSON format request
            logger.info(f"Extracting story components from document {document.id}")
            response = await self.ollama_service.generate(
                prompt=user_prompt,
                system_prompt=self.SYSTEM_PROMPT,
                format_json=True,
            )

            # Parse JSON response
            try:
                extracted_data = json.loads(response["content"])
            except json.JSONDecodeError as e:
                logger.warning(
                    f"JSON parse failed for document {document.id}: {e}. Attempting regex fallback."
                )
                extracted_data = self._regex_fallback(document.content)

            # Calculate confidence score based on field completeness
            confidence = self._calculate_confidence(extracted_data)

            # Create and return schema
            return ExtractedStorySchema(
                role=extracted_data.get("role"),
                action=extracted_data.get("action"),
                benefit=extracted_data.get("benefit"),
                acceptance_criteria=extracted_data.get("acceptance_criteria"),
                status=self._normalize_status(extracted_data.get("status")),
                confidence_score=confidence,
            )

        except Exception as e:
            # Never fail - return extraction_failed result
            logger.error(
                f"Story extraction failed for document {document.id}: {e}",
                exc_info=True,
            )
            return ExtractedStorySchema(
                role=None,
                action=None,
                benefit=None,
                acceptance_criteria=None,
                status=None,
                confidence_score=0.0,
            )

    def _regex_fallback(self, content: str) -> dict:
        """Regex-based fallback for basic field extraction when LLM JSON fails.

        Args:
            content: Markdown content

        Returns:
            Dict with extracted fields (may contain None values)
        """
        result = {
            "role": None,
            "action": None,
            "benefit": None,
            "acceptance_criteria": None,
            "status": None,
        }

        # Extract role: "As a [role]" or "**As a** [role]"
        role_match = re.search(
            r"\*?\*?As a\*?\*?\s+(.+?)(?:,|\n)", content, re.IGNORECASE
        )
        if role_match:
            result["role"] = role_match.group(1).strip()

        # Extract action: "I want [action]" or "**I want** [action]"
        action_match = re.search(
            r"\*?\*?I want\*?\*?\s+(.+?)(?:,|\n|so that)", content, re.IGNORECASE
        )
        if action_match:
            result["action"] = action_match.group(1).strip()

        # Extract benefit: "so that [benefit]" or "**so that** [benefit]"
        benefit_match = re.search(
            r"\*?\*?so that\*?\*?\s+(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if benefit_match:
            result["benefit"] = benefit_match.group(1).strip()

        # Extract acceptance criteria: numbered list items
        ac_matches = re.findall(r"^\d+\.\s+(.+)$", content, re.MULTILINE)
        if ac_matches:
            result["acceptance_criteria"] = ac_matches

        # Extract status: "Status: Draft" or "**Status:** Dev"
        status_match = re.search(
            r"\*?\*?Status:?\*?\*?\s*(Draft|Dev|Done)", content, re.IGNORECASE
        )
        if status_match:
            result["status"] = status_match.group(1).lower()

        return result

    def _calculate_confidence(self, extracted_data: dict) -> float:
        """Calculate confidence score based on field completeness.

        Scoring:
        - All 5 fields present = 1.0
        - 4 fields = 0.8
        - 3 fields = 0.6
        - 2 fields = 0.4
        - 1 field = 0.2
        - 0 fields = 0.0

        Args:
            extracted_data: Dict with extracted fields

        Returns:
            Confidence score (0.0-1.0)
        """
        fields = ["role", "action", "benefit", "acceptance_criteria", "status"]
        populated_count = sum(
            1 for field in fields if extracted_data.get(field) not in (None, [], "")
        )

        confidence_map = {
            5: 1.0,
            4: 0.8,
            3: 0.6,
            2: 0.4,
            1: 0.2,
            0: 0.0,
        }

        return confidence_map.get(populated_count, 0.0)

    def _normalize_status(self, status: Optional[str]) -> Optional[str]:
        """Normalize status value to lowercase enum values.

        Args:
            status: Raw status string from extraction

        Returns:
            Normalized status ("draft", "dev", "done") or None
        """
        if not status:
            return None

        status_lower = status.lower().strip()
        if status_lower in ("draft", "dev", "done"):
            return status_lower

        return None
