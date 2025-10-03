"""Document API routes."""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..repositories.document_repository import DocumentRepository
from ..schemas.document import (
    DocumentListResponse,
    DocumentDetailResponse,
    DocumentResolveResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])


@router.get(
    "/projects/{project_id}/documents",
    response_model=List[DocumentListResponse],
    status_code=status.HTTP_200_OK,
)
async def get_project_documents(
    project_id: UUID,
    type: Optional[str] = Query(
        None,
        description="Filter by document type (scoping, architecture, epic, story, qa, other)",
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get documents for a project, optionally filtered by type.

    Args:
        project_id: Project UUID
        type: Optional document type filter
        db: Database session

    Returns:
        List of documents (without full content)

    Raises:
        HTTPException: 404 if project not found
    """
    doc_repo = DocumentRepository(db)

    # Verify project exists
    from ..repositories.project_repository import ProjectRepository

    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Get documents
    documents = await doc_repo.get_by_type(project_id, type)
    return documents


@router.get(
    "/documents/{document_id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get single document with full content.

    Args:
        document_id: Document UUID
        db: Database session

    Returns:
        Document with full content

    Raises:
        HTTPException: 404 if document not found
    """
    doc_repo = DocumentRepository(db)
    document = await doc_repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found",
        )

    return document


@router.get(
    "/documents/resolve",
    response_model=DocumentResolveResponse,
    status_code=status.HTTP_200_OK,
)
async def resolve_document_path(
    file_path: str = Query(..., description="File path to resolve"),
    project_id: UUID = Query(..., description="Project UUID"),
    db: AsyncSession = Depends(get_db),
):
    """Resolve file path to document ID.

    Handles relative paths (../, ./) and absolute paths.

    Args:
        file_path: File path (relative or absolute)
        project_id: Project UUID
        db: Database session

    Returns:
        Document ID and metadata

    Raises:
        HTTPException: 404 if document not found
    """
    doc_repo = DocumentRepository(db)
    document = await doc_repo.resolve_path(project_id, file_path)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found for path: {file_path}",
        )

    return document
