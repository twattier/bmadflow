"""Search request and response schemas for vector similarity search API."""

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """Request schema for vector similarity search.

    Attributes:
        query: Search query text (minimum 1 character)
        top_k: Number of results to return (default 5, range 1-20)
    """

    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return (max 20)")

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, v: int) -> int:
        """Validate top_k is within allowed range.

        Args:
            v: The top_k value to validate

        Returns:
            The validated top_k value

        Raises:
            ValueError: If top_k is not between 1 and 20
        """
        if v < 1 or v > 20:
            raise ValueError("top_k must be between 1 and 20")
        return v

    class Config:
        """Pydantic configuration with OpenAPI example."""

        json_schema_extra = {"example": {"query": "How does the RAG pipeline work?", "top_k": 5}}


class SearchResult(BaseModel):
    """Individual search result with similarity score.

    Attributes:
        chunk_id: Unique identifier for the chunk
        document_id: ID of the parent document
        chunk_text: Content of the chunk
        similarity_score: Cosine similarity score (0.0-1.0, higher is more similar)
        header_anchor: Markdown header anchor for navigation (optional)
        metadata: Additional metadata from chunk (file_path, file_name, etc.)
    """

    chunk_id: UUID
    document_id: UUID
    chunk_text: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    header_anchor: str | None = None
    metadata: dict


class SearchResponse(BaseModel):
    """Response schema containing search results.

    Attributes:
        query: Original search query
        results: List of matching chunks with similarity scores
        total_results: Total number of results returned
    """

    query: str
    results: List[SearchResult]
    total_results: int

    class Config:
        """Pydantic configuration with OpenAPI example."""

        json_schema_extra = {
            "example": {
                "query": "How does the RAG pipeline work?",
                "results": [
                    {
                        "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                        "document_id": "660e8400-e29b-41d4-a716-446655440000",
                        "chunk_text": "The RAG pipeline integrates Docling for document processing...",
                        "similarity_score": 0.89,
                        "header_anchor": "rag-pipeline",
                        "metadata": {
                            "file_path": "docs/architecture.md",
                            "file_name": "architecture.md",
                            "file_type": "md",
                        },
                    }
                ],
                "total_results": 1,
            }
        }
