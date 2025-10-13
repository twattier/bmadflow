"""Pydantic schemas for agent requests and responses."""

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RAGQueryRequest(BaseModel):
    """Request schema for RAG agent query."""

    user_message: str = Field(..., min_length=1, description="User's question or query")
    project_id: UUID = Field(..., description="Project UUID to search within")
    conversation_id: UUID = Field(..., description="Conversation UUID for context")
    llm_provider_id: UUID = Field(
        ..., description="LLM provider UUID to use for response generation"
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")

    @field_validator("user_message")
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        """Validate user message is not empty after stripping."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("user_message cannot be empty")
        return stripped

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "user_message": "What are the main goals of this project?",
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
                "llm_provider_id": "770e8400-e29b-41d4-a716-446655440000",
                "top_k": 5,
            }
        }


class SourceAttribution(BaseModel):
    """Source attribution for RAG response."""

    document_id: UUID = Field(..., description="Document UUID from database")
    file_path: str = Field(..., description="Relative file path (e.g., docs/prd.md)")
    header_anchor: str | None = Field(
        None, description="Section anchor if available (e.g., 'goals')"
    )
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")

    def format_link(self) -> str:
        """Format as markdown link for frontend display.

        Returns:
            Markdown link: [filename.md#section](document_id#anchor) or [filename.md](document_id)
        """
        filename = self.file_path.split("/")[-1]
        if self.header_anchor:
            return f"[{filename}#{self.header_anchor}]({self.document_id}#{self.header_anchor})"
        else:
            return f"[{filename}]({self.document_id})"

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "file_path": "docs/prd.md",
                "header_anchor": "goals",
                "similarity_score": 0.8523,
            }
        }


class RAGResponse(BaseModel):
    """Response schema for RAG agent."""

    response_text: str = Field(..., description="Generated response from LLM")
    sources: List[SourceAttribution] = Field(
        default_factory=list, description="Source documents used in response"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "response_text": "The main goals of this project are to...",
                "sources": [
                    {
                        "document_id": "550e8400-e29b-41d4-a716-446655440000",
                        "file_path": "docs/prd.md",
                        "header_anchor": "goals",
                        "similarity_score": 0.8523,
                    }
                ],
            }
        }
