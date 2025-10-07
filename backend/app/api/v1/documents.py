"""Document API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_document_service
from app.schemas.document import FileTreeResponse
from app.services.document_service import DocumentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/projects/{project_id}/file-tree", response_model=FileTreeResponse)
async def get_file_tree(
    project_id: UUID,
    document_service: DocumentService = Depends(get_document_service),
):
    """Get hierarchical file tree for project documents.

    Args:
        project_id: Project UUID
        document_service: Injected document service

    Returns:
        FileTreeResponse with hierarchical tree structure

    Raises:
        HTTPException: 500 if tree building fails
    """
    try:
        tree = await document_service.build_file_tree(project_id)
        return tree
    except Exception as e:
        logger.error(f"Failed to build file tree for project {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to build file tree: {str(e)}")
