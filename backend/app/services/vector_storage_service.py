"""Vector storage service for embedding persistence."""

import logging
from typing import List, Optional
from uuid import UUID

from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository
from app.schemas.chunk import ChunkCreate

logger = logging.getLogger(__name__)


class VectorStorageService:
    """Service for storing vector embeddings with metadata."""

    def __init__(self, chunk_repository: ChunkRepository):
        """Initialize service with chunk repository dependency.

        Args:
            chunk_repository: Chunk data access repository
        """
        self.chunk_repo = chunk_repository

    async def store_chunk(
        self,
        document_id: UUID,
        chunk_text: str,
        chunk_index: int,
        embedding: List[float],
        header_anchor: Optional[str],
        file_path: str,
        file_name: str,
        file_type: str,
        total_chunks: int,
    ) -> Chunk:
        """Store a single chunk with embedding and metadata.

        Args:
            document_id: UUID of parent document
            chunk_text: Text content of chunk
            chunk_index: 0-based position in document
            embedding: 768-dimensional vector embedding
            header_anchor: Markdown section anchor (nullable)
            file_path: Relative path to source file
            file_name: File name
            file_type: File extension (md, csv, yaml, json)
            total_chunks: Total number of chunks in document

        Returns:
            Created Chunk ORM object

        Raises:
            ValueError: If embedding dimension != 768
            IntegrityError: If document_id does not exist
        """
        # Validate embedding dimension
        if len(embedding) != 768:
            raise ValueError(f"Embedding must be 768 dimensions, got {len(embedding)}")

        # Construct metadata per AC4
        metadata = {
            "file_path": file_path,
            "file_name": file_name,
            "file_type": file_type,
            "chunk_position": chunk_index,
            "total_chunks": total_chunks,
        }

        chunk_data = ChunkCreate(
            document_id=document_id,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
            embedding=embedding,
            header_anchor=header_anchor,
            metadata=metadata,
        )

        chunk = await self.chunk_repo.create_chunk(chunk_data)

        if header_anchor:
            logger.info(
                f"Stored chunk {chunk.id} with embedding (dim={len(embedding)}) "
                f"and header anchor: {header_anchor}"
            )
        else:
            logger.info(f"Stored chunk {chunk.id} with embedding (dim={len(embedding)})")

        return chunk

    async def store_chunks_batch(self, chunks_data: List[dict]) -> List[Chunk]:
        """Optimized bulk insert for multiple chunks.

        Args:
            chunks_data: List of chunk dictionaries with all required fields

        Returns:
            List of created chunk instances

        Raises:
            ValueError: If any embedding dimension != 768
            ValidationError: If chunk data is invalid
        """
        chunk_creates = [ChunkCreate(**data) for data in chunks_data]
        chunks = await self.chunk_repo.create_chunks_batch(chunk_creates)
        logger.info(f"Stored {len(chunks)} chunks in batch")
        return chunks
