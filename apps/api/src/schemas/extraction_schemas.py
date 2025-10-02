"""Pydantic schemas for LLM extraction results."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ExtractedStorySchema(BaseModel):
    """Schema for extracted user story components.

    Used by StoryExtractionService to enforce structured LLM output.
    All fields are optional to handle partial extraction gracefully.
    """

    role: Optional[str] = Field(
        None,
        description="User role from 'As a [role]' statement",
        max_length=500,
    )
    action: Optional[str] = Field(
        None,
        description="Desired capability from 'I want [action]' statement",
        max_length=1000,
    )
    benefit: Optional[str] = Field(
        None,
        description="Business value from 'So that [benefit]' statement",
        max_length=1000,
    )
    acceptance_criteria: Optional[List[str]] = Field(
        None,
        description="List of acceptance criteria items",
    )
    status: Optional[Literal["draft", "dev", "done"]] = Field(
        None,
        description="Story status extracted from Status marker or inferred",
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence (0.0-1.0) based on field completeness",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "backend developer",
                "action": "extract user story components from markdown",
                "benefit": "structured data can be displayed in dashboard",
                "acceptance_criteria": [
                    "Extraction service accepts markdown content",
                    "Service generates prompt for LLM",
                ],
                "status": "draft",
                "confidence_score": 1.0,
            }
        }
    }


class ExtractedEpicSchema(BaseModel):
    """Schema for extracted epic metadata.

    Used by EpicExtractionService to enforce structured LLM output.
    All fields except title are optional to handle partial extraction gracefully.
    """

    epic_number: Optional[int] = Field(
        None,
        description="Epic number extracted from title (e.g., 'Epic 2' -> 2)",
    )
    title: str = Field(
        ...,
        description="Epic title extracted from heading",
        max_length=500,
    )
    goal: Optional[str] = Field(
        None,
        description="Epic goal/description from Epic Goal or Epic Description section",
    )
    status: Optional[Literal["draft", "dev", "done"]] = Field(
        None,
        description="Epic status extracted from Status marker or inferred",
    )
    related_stories: Optional[List[str]] = Field(
        None,
        description="List of story file paths from markdown links",
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence (0.0-1.0) based on field completeness",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "epic_number": 2,
                "title": "LLM-Powered Content Extraction",
                "goal": "Implement OLLAMA-based extraction of structured information from BMAD markdown",
                "status": "dev",
                "related_stories": ["stories/story-2-1.md", "stories/story-2-2.md"],
                "confidence_score": 1.0,
            }
        }
    }
