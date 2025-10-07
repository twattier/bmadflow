"""Document Pydantic schemas."""

import uuid
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema."""

    file_path: str
    file_type: str
    file_size: int
    doc_metadata: Optional[dict] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    project_doc_id: uuid.UUID
    content: str


class DocumentResponse(DocumentBase):
    """Response model for document metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_doc_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class FileTreeNode(BaseModel):
    """File tree node representing a file or folder."""

    type: Literal["file", "folder"]
    name: str
    path: str
    children: Optional[List["FileTreeNode"]] = None
    id: Optional[uuid.UUID] = None
    file_type: Optional[str] = None
    size: Optional[int] = None


class FileTreeResponse(BaseModel):
    """Response model for file tree."""

    project_id: uuid.UUID
    tree: List[FileTreeNode]
