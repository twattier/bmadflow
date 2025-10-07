"""Document repository for data access."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentCreate


class DocumentRepository:
    """Repository for Document database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(self, document_data: DocumentCreate) -> Document:
        """Insert new document.

        Args:
            document_data: Document creation data

        Returns:
            Created document instance
        """
        document = Document(**document_data.model_dump())
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def upsert(
        self,
        project_doc_id: UUID,
        file_path: str,
        content: str,
        file_type: str,
        file_size: int,
        commit_sha: str,
        metadata: Optional[dict] = None,
    ) -> Document:
        """Insert or update document (upsert pattern).

        Args:
            project_doc_id: ProjectDoc UUID
            file_path: Relative file path within repository
            content: File content as string
            file_type: File extension/type
            file_size: File size in bytes
            commit_sha: GitHub commit SHA
            metadata: Optional metadata dictionary

        Returns:
            Created or updated document instance
        """
        # Check if document exists
        result = await self.db.execute(
            select(Document).where(
                Document.project_doc_id == project_doc_id, Document.file_path == file_path
            )
        )
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            # Update existing document
            existing_doc.content = content
            existing_doc.file_size = file_size
            existing_doc.file_type = file_type
            existing_doc.doc_metadata = metadata or {}
            existing_doc.doc_metadata["github_commit_sha"] = commit_sha
            existing_doc.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing_doc)
            return existing_doc
        else:
            # Insert new document
            new_doc = Document(
                project_doc_id=project_doc_id,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                content=content,
                doc_metadata={"github_commit_sha": commit_sha, **(metadata or {})},
            )
            self.db.add(new_doc)
            await self.db.commit()
            await self.db.refresh(new_doc)
            return new_doc

    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Retrieve document by ID.

        Args:
            document_id: Document UUID

        Returns:
            Document instance if found, None otherwise
        """
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_by_project_doc(self, project_doc_id: UUID) -> List[Document]:
        """Get all documents for a ProjectDoc.

        Args:
            project_doc_id: ProjectDoc UUID

        Returns:
            List of documents for the ProjectDoc
        """
        result = await self.db.execute(
            select(Document).where(Document.project_doc_id == project_doc_id)
        )
        return list(result.scalars().all())

    async def count_by_project_doc(self, project_doc_id: UUID) -> int:
        """Count documents for a ProjectDoc.

        Args:
            project_doc_id: ProjectDoc UUID

        Returns:
            Number of documents for the ProjectDoc
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.project_doc_id == project_doc_id)
        )
        return result.scalar() or 0

    async def delete_by_project_doc(self, project_doc_id: UUID) -> int:
        """Delete all documents for a ProjectDoc (for re-sync).

        Args:
            project_doc_id: ProjectDoc UUID

        Returns:
            Number of documents deleted
        """
        result = await self.db.execute(
            select(Document).where(Document.project_doc_id == project_doc_id)
        )
        documents = result.scalars().all()
        count = len(documents)

        for doc in documents:
            await self.db.delete(doc)

        await self.db.commit()
        return count
