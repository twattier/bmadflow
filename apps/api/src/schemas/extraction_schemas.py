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
