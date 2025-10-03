"""Epic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ExtractedEpicData(BaseModel):
    """Nested extracted epic metadata."""

    status: str = Field(..., description="Epic status: draft, dev, or done")
    story_count: int = Field(0, description="Number of stories in this epic")

    class Config:
        from_attributes = True


class EpicResponse(BaseModel):
    """Response schema for epic with document and extracted data."""

    # Document fields
    id: UUID
    project_id: UUID
    file_path: str
    content: str
    doc_type: str
    title: str
    excerpt: Optional[str] = None
    last_modified: Optional[datetime] = None

    # Nested extracted_epic data
    extracted_epic: Optional[ExtractedEpicData] = Field(
        None, description="Extracted epic metadata, null if not yet extracted"
    )

    class Config:
        from_attributes = True
