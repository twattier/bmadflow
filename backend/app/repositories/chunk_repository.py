"""Chunk repository for data access."""

import logging
from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.project_doc import ProjectDoc
from app.schemas.chunk import ChunkCreate

logger = logging.getLogger(__name__)


class ChunkRepository:
    """Repository for Chunk database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_chunk(self, chunk_data: ChunkCreate) -> Chunk:
        """Insert a single chunk into the database.

        Args:
            chunk_data: Chunk creation data

        Returns:
            Created chunk instance

        Raises:
            IntegrityError: If document_id does not exist (foreign key violation)
        """
        chunk = Chunk(**chunk_data.model_dump())
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        logger.info(f"Created chunk {chunk.id} for document {chunk.document_id}")
        return chunk

    async def create_chunks_batch(
        self, chunks: List[ChunkCreate], auto_commit: bool = True
    ) -> List[Chunk]:
        """Bulk insert chunks for performance.

        Args:
            chunks: List of chunk creation data
            auto_commit: Whether to commit automatically (default True for backward compatibility)

        Returns:
            List of created chunk instances

        Raises:
            IntegrityError: If any document_id does not exist
        """
        chunk_objs = [Chunk(**chunk.model_dump()) for chunk in chunks]
        self.db.add_all(chunk_objs)
        if auto_commit:
            await self.db.commit()
            # Refresh all chunks to load their metadata from the database
            for chunk in chunk_objs:
                await self.db.refresh(chunk)
        logger.info(f"Created {len(chunk_objs)} chunks in batch")
        return chunk_objs

    async def get_by_document_id(self, document_id: UUID) -> List[Chunk]:
        """Retrieve all chunks for a document in order.

        Args:
            document_id: Document UUID

        Returns:
            List of chunks ordered by chunk_index
        """
        result = await self.db.execute(
            select(Chunk).where(Chunk.document_id == document_id).order_by(Chunk.chunk_index)
        )
        return list(result.scalars().all())

    async def count_by_project_id(self, project_id: UUID) -> int:
        """Count total chunks for a project (dashboard metric).

        Args:
            project_id: Project UUID

        Returns:
            Total number of chunks across all documents in the project
        """
        # Join through document → project_doc → project
        result = await self.db.execute(
            select(func.count(Chunk.id))
            .join(Document, Chunk.document_id == Document.id)
            .join(ProjectDoc, Document.project_doc_id == ProjectDoc.id)
            .where(ProjectDoc.project_id == project_id)
        )
        return result.scalar() or 0
