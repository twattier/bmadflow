"""Epic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DocumentInfo(BaseModel):
    """Embedded document info in epic response."""

    file_path: str
    last_modified: Optional[datetime] = None

    class Config:
        from_attributes = True


class EpicListResponse(BaseModel):
    """Response schema for epic list with extracted metadata."""

    id: UUID
    document_id: UUID
    epic_number: Optional[int] = None
    title: str
    goal: Optional[str] = None
    status: str
    story_count: int
    confidence_score: Optional[float] = None
    extracted_at: datetime
    document: DocumentInfo

    class Config:
        from_attributes = True
