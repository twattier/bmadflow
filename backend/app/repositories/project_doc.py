"""ProjectDoc repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_doc import ProjectDoc
from app.schemas.project_doc import ProjectDocCreate, ProjectDocUpdate


class ProjectDocRepository:
    """Repository for ProjectDoc database operations."""

    async def create(
        self, db: AsyncSession, project_id: UUID, data: ProjectDocCreate
    ) -> ProjectDoc:
        """Create a new ProjectDoc."""
        data_dict = data.model_dump()
        # Convert HttpUrl to string for database storage
        if "github_url" in data_dict:
            data_dict["github_url"] = str(data_dict["github_url"])
        project_doc = ProjectDoc(project_id=project_id, **data_dict)
        db.add(project_doc)
        await db.commit()
        await db.refresh(project_doc)
        return project_doc

    async def get_all_by_project(self, db: AsyncSession, project_id: UUID) -> List[ProjectDoc]:
        """Get all ProjectDocs for a Project ordered by created_at DESC."""
        result = await db.execute(
            select(ProjectDoc)
            .where(ProjectDoc.project_id == project_id)
            .order_by(ProjectDoc.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, id: UUID) -> Optional[ProjectDoc]:
        """Get ProjectDoc by ID."""
        result = await db.execute(select(ProjectDoc).where(ProjectDoc.id == id))
        return result.scalar_one_or_none()

    async def get_by_name_and_project(
        self, db: AsyncSession, project_id: UUID, name: str
    ) -> Optional[ProjectDoc]:
        """Get ProjectDoc by name within a specific project."""
        result = await db.execute(
            select(ProjectDoc).where(ProjectDoc.project_id == project_id, ProjectDoc.name == name)
        )
        return result.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, id: UUID, data: ProjectDocUpdate
    ) -> Optional[ProjectDoc]:
        """Update ProjectDoc by ID."""
        project_doc = await self.get_by_id(db, id)
        if not project_doc:
            return None

        data_dict = data.model_dump(exclude_unset=True)
        # Convert HttpUrl to string for database storage
        if "github_url" in data_dict:
            data_dict["github_url"] = str(data_dict["github_url"])

        for key, value in data_dict.items():
            setattr(project_doc, key, value)

        await db.commit()
        await db.refresh(project_doc)
        return project_doc

    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """Delete ProjectDoc by ID."""
        result = await db.execute(delete(ProjectDoc).where(ProjectDoc.id == id))
        await db.commit()
        return result.rowcount > 0
