"""Epic repository for database access."""

from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.document import Document
from .base_repository import BaseRepository


class EpicRepository(BaseRepository[Document]):
    """Repository for Epic document operations."""

    def __init__(self, db: AsyncSession):
        """Initialize epic repository.

        Args:
            db: Async database session
        """
        super().__init__(Document, db)

    async def get_by_project(self, project_id: UUID) -> List[Document]:
        """Get all epic documents for a project with extracted epic data.

        Args:
            project_id: Project UUID

        Returns:
            List of Document instances (doc_type='epic') with extracted_epic relationship loaded
        """
        from ..models.extracted_epic import ExtractedEpic

        # Fetch documents
        doc_query = (
            select(Document)
            .where(Document.project_id == project_id)
            .where(Document.doc_type == "epic")
            .order_by(Document.file_path)
        )
        doc_result = await self.db.execute(doc_query)
        documents = list(doc_result.scalars().all())

        if not documents:
            return []

        # Fetch extracted_epics for these documents
        doc_ids = [doc.id for doc in documents]
        epic_query = select(ExtractedEpic).where(ExtractedEpic.document_id.in_(doc_ids))
        epic_result = await self.db.execute(epic_query)
        extracted_epics = {epic.document_id: epic for epic in epic_result.scalars().all()}

        # Manually attach extracted_epics to documents
        for doc in documents:
            doc.extracted_epic = extracted_epics.get(doc.id)

        return documents
