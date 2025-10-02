"""Document repository for database access."""

from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from ..models.document import Document
from .base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model operations."""

    def __init__(self, db: AsyncSession):
        """Initialize document repository.

        Args:
            db: Async database session
        """
        super().__init__(Document, db)

    async def get_by_project_id(self, project_id: UUID) -> List[Document]:
        """Get all documents for a project.

        Args:
            project_id: Project UUID

        Returns:
            List of document instances
        """
        result = await self.db.execute(
            select(Document).where(Document.project_id == project_id)
        )
        return list(result.scalars().all())

    async def upsert(self, **kwargs) -> Document:
        """Insert or update document based on unique constraint (project_id, file_path).

        Args:
            **kwargs: Document field values

        Returns:
            Upserted document instance
        """
        stmt = insert(Document).values(**kwargs)
        stmt = stmt.on_conflict_do_update(
            index_elements=["project_id", "file_path"],
            set_={
                "content": stmt.excluded.content,
                "doc_type": stmt.excluded.doc_type,
                "title": stmt.excluded.title,
                "excerpt": stmt.excluded.excerpt,
                "last_modified": stmt.excluded.last_modified,
            },
        )
        result = await self.db.execute(stmt.returning(Document))
        await self.db.commit()
        return result.scalar_one()
