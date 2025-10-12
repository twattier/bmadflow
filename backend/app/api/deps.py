"""Dependency injection for API endpoints."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


async def get_document_service(
    db: AsyncSession = Depends(get_db),
) -> DocumentService:
    """Get document service with injected dependencies.

    Args:
        db: Database session

    Returns:
        DocumentService instance
    """
    document_repo = DocumentRepository(db)
    return DocumentService(document_repo)


async def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance.

    Returns:
        EmbeddingService instance configured with settings
    """
    return EmbeddingService()


async def get_chunk_repository(db: AsyncSession = Depends(get_db)) -> ChunkRepository:
    """Get chunk repository with injected database session.

    Args:
        db: Database session

    Returns:
        ChunkRepository instance
    """
    return ChunkRepository(db)
