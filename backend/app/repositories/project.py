"""Repository layer for Project data access."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Repository for Project CRUD operations."""

    async def create(self, db: AsyncSession, data: ProjectCreate) -> Project:
        """Create a new project.

        Args:
            db: Database session
            data: Project creation data

        Returns:
            Created project instance
        """
        project = Project(**data.model_dump())
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    async def get_all(self, db: AsyncSession) -> List[Project]:
        """Get all projects ordered by created_at DESC.

        Args:
            db: Database session

        Returns:
            List of all projects
        """
        result = await db.execute(select(Project).order_by(Project.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, project_id: UUID) -> Optional[Project]:
        """Get project by ID.

        Args:
            db: Database session
            project_id: Project UUID

        Returns:
            Project instance or None if not found
        """
        result = await db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, project_id: UUID, data: ProjectUpdate
    ) -> Optional[Project]:
        """Update project by ID.

        Args:
            db: Database session
            project_id: Project UUID
            data: Project update data

        Returns:
            Updated project instance or None if not found
        """
        project = await self.get_by_id(db, project_id)
        if not project:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(project, key, value)

        await db.commit()
        await db.refresh(project)
        return project

    async def delete(self, db: AsyncSession, project_id: UUID) -> bool:
        """Delete project by ID.

        Args:
            db: Database session
            project_id: Project UUID

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(delete(Project).where(Project.id == project_id))
        await db.commit()
        return result.rowcount > 0
