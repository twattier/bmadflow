"""Project repository for database access."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.project import Project
from .base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model operations."""

    def __init__(self, db: AsyncSession):
        """Initialize project repository.

        Args:
            db: Async database session
        """
        super().__init__(Project, db)

    async def get_by_github_url(self, github_url: str) -> Optional[Project]:
        """Get project by GitHub URL.

        Args:
            github_url: GitHub repository URL

        Returns:
            Project instance or None if not found
        """
        result = await self.db.execute(
            select(Project).where(Project.github_url == github_url)
        )
        return result.scalar_one_or_none()
