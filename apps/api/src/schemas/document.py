"""Document schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema with common fields."""

    file_path: str
    doc_type: str
    title: str
    excerpt: Optional[str] = None
    last_modified: Optional[datetime] = None
    extraction_status: str
    extraction_confidence: Optional[float] = None


class DocumentListResponse(DocumentBase):
    """Response schema for document list (without full content)."""

    id: UUID
    project_id: UUID

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentBase):
    """Response schema for single document (with full content)."""

    id: UUID
    project_id: UUID
    content: str

    class Config:
        from_attributes = True


class DocumentResolveResponse(BaseModel):
    """Response schema for document path resolution."""

    id: UUID
    file_path: str
    title: str
    doc_type: str

    class Config:
        from_attributes = True
