"""Get document content tool for RAG agent."""

import logging
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse

logger = logging.getLogger(__name__)


class GetDocumentTool(BaseModel):
    """Tool for retrieving full document content by document ID."""

    document_id: UUID = Field(..., description="Document UUID to retrieve")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    async def execute(self, db: AsyncSession) -> DocumentResponse | None:
        """Execute document retrieval.

        Args:
            db: Database session

        Returns:
            DocumentResponse with full content and metadata, or None if not found

        Raises:
            ValueError: If document_id is invalid
        """
        logger.info(f"Retrieving document: {self.document_id}")

        # Fetch document from repository
        document_repo = DocumentRepository(db)
        document = await document_repo.get_by_id(self.document_id)

        if not document:
            logger.warning(f"Document not found: {self.document_id}")
            return None

        # Convert to response schema
        response = DocumentResponse(
            id=document.id,
            project_doc_id=document.project_doc_id,
            file_path=document.file_path,
            file_type=document.file_type,
            file_size=document.file_size,
            content=document.content,
            commit_sha=document.commit_sha,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

        logger.info(f"Document retrieved: {document.file_path} ({document.file_size} bytes)")
        return response
