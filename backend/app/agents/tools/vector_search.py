"""Vector search tool for RAG agent."""

import logging
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class ChunkResult(BaseModel):
    """Chunk search result with metadata."""

    chunk_id: UUID = Field(..., description="Chunk UUID")
    document_id: UUID = Field(..., description="Parent document UUID")
    chunk_text: str = Field(..., description="Chunk text content")
    file_path: str = Field(..., description="Relative file path")
    header_anchor: str | None = Field(None, description="Markdown header anchor if available")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score")
    chunk_index: int = Field(..., description="Position in document")


class VectorSearchTool(BaseModel):
    """Tool for retrieving relevant document chunks via vector similarity search."""

    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    similarity_threshold: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Minimum similarity score"
    )

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    async def execute(self, project_id: UUID, db: AsyncSession) -> List[ChunkResult]:
        """Execute vector similarity search.

        Args:
            project_id: Project UUID to filter results
            db: Database session

        Returns:
            List of ChunkResult objects sorted by relevance (highest first)

        Raises:
            ConnectionError: If Ollama service unavailable
            ValueError: If embedding generation fails
        """
        logger.info(f"Executing vector search: query='{self.query}', top_k={self.top_k}")

        # Generate query embedding
        embedding_service = EmbeddingService()
        query_embedding = await embedding_service.generate_embedding(self.query)

        # Perform similarity search
        chunk_repo = ChunkRepository(db)
        results = await chunk_repo.similarity_search(query_embedding, project_id, self.top_k)

        # Convert to ChunkResult objects with filtering
        chunk_results = []
        for chunk, similarity in results:
            if similarity >= self.similarity_threshold:
                # Get file_path from the related document
                file_path = chunk.document.file_path if chunk.document else ""

                chunk_results.append(
                    ChunkResult(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        chunk_text=chunk.chunk_text,
                        file_path=file_path,
                        header_anchor=chunk.header_anchor,
                        similarity_score=round(similarity, 4),
                        chunk_index=chunk.chunk_index,
                    )
                )

        logger.info(
            f"Vector search completed: found {len(chunk_results)}/{len(results)} chunks "
            f"above threshold {self.similarity_threshold}"
        )

        return chunk_results
