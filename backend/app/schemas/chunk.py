"""Chunk schema for vector embeddings."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChunkCreate(BaseModel):
    """Request model for creating a chunk with embedding.

    Attributes:
        document_id: UUID of parent document
        chunk_text: Text content of chunk
        chunk_index: 0-based position in document
        embedding: 768-dimensional vector embedding
        header_anchor: Markdown section anchor (nullable)
        metadata: JSONB metadata with file info
    """

    document_id: uuid.UUID
    chunk_text: str = Field(..., min_length=1)
    chunk_index: int = Field(..., ge=0)
    embedding: List[float] = Field(..., min_length=768, max_length=768)
    header_anchor: Optional[str] = Field(None, max_length=512)
    metadata: Optional[dict] = None

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimension(cls, v: List[float]) -> List[float]:
        """Ensure embedding is exactly 768 dimensions."""
        if len(v) != 768:
            raise ValueError(f"Embedding must be 768 dimensions, got {len(v)}")
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata_structure(cls, v: Optional[dict]) -> Optional[dict]:
        """Validate metadata contains required fields."""
        if v is not None:
            required_fields = [
                "file_path",
                "file_name",
                "file_type",
                "chunk_position",
                "total_chunks",
            ]
            missing = [f for f in required_fields if f not in v]
            if missing:
                raise ValueError(f"Metadata missing required fields: {missing}")
        return v


class ChunkProcessed(BaseModel):
    """Schema for chunks processed by DoclingService (before storage).

    Used as intermediate representation between document processing
    and database storage. Does not include database fields like id, created_at.
    """

    text: str = Field(..., min_length=1)
    index: int = Field(..., ge=0)
    header_anchor: Optional[str] = Field(None, max_length=512)
    metadata: Optional[Dict] = None


class ChunkResponse(BaseModel):
    """Response model for chunk data from database.

    Note: Embedding not included in response (too large for API).
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_text: str
    chunk_index: int
    header_anchor: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
