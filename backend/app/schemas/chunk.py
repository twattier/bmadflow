"""Chunk schema for document processing."""

from pydantic import BaseModel, Field


class ChunkResponse(BaseModel):
    """Response model for document chunks.

    Represents a single chunk of processed document content with metadata
    for tracking position and context within the source document.

    Attributes:
        text: The actual chunk content as a string
        index: Zero-based order of the chunk within the document
        metadata: Additional information about the chunk including:
            - file_path: Source file path (if applicable)
            - file_type: File extension (md, csv, yaml, json)
            - position: Character position in original document
            - total_chunks: Total number of chunks for this document
            - headers: Markdown headers context (for markdown files)
    """

    text: str = Field(..., description="Chunk content text")
    index: int = Field(..., ge=0, description="Zero-based chunk order")
    metadata: dict = Field(default_factory=dict, description="Additional chunk metadata")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "text": "# Introduction\\n\\nThis is a sample document.",
                "index": 0,
                "metadata": {
                    "file_type": "md",
                    "position": 0,
                    "total_chunks": 5,
                    "headers": ["Introduction"],
                },
            }
        }
