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

    async def get_by_type(
        self, project_id: UUID, doc_type: str = None
    ) -> List[Document]:
        """Get documents filtered by type.

        Args:
            project_id: Project UUID
            doc_type: Optional document type filter

        Returns:
            List of documents ordered by file_path
        """
        query = select(Document).where(Document.project_id == project_id)

        if doc_type:
            query = query.where(Document.doc_type == doc_type)

        query = query.order_by(Document.file_path)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def resolve_path(
        self, project_id: UUID, file_path: str
    ) -> Document | None:
        """Resolve file path to document ID.

        Handles relative paths (../, ./) by normalizing to absolute path.

        Args:
            project_id: Project UUID
            file_path: File path (relative or absolute)

        Returns:
            Document if found, None otherwise
        """
        # Normalize path
        normalized = file_path.lstrip("/")

        # Handle relative paths
        if normalized.startswith("../"):
            normalized = normalized.replace("../", "")
        if normalized.startswith("./"):
            normalized = normalized.replace("./", "")

        # Ensure path starts with 'docs/'
        if not normalized.startswith("docs/"):
            normalized = f"docs/{normalized}"

        # Query database
        result = await self.db.execute(
            select(Document).where(
                Document.project_id == project_id, Document.file_path == normalized
            )
        )
        return result.scalar_one_or_none()
