"""Dependency injection for API endpoints."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService


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
