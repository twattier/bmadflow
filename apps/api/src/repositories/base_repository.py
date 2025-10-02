"""Base repository with generic CRUD operations."""

from typing import Generic, TypeVar, Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository for database operations."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        """Initialize repository with model and database session.

        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID.

        Args:
            id: Entity UUID

        Returns:
            Entity instance or None if not found
        """
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entity instances
        """
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        """Create new entity.

        Args:
            **kwargs: Entity field values

        Returns:
            Created entity instance
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """Update existing entity.

        Args:
            id: Entity UUID
            **kwargs: Fields to update

        Returns:
            Updated entity instance or None if not found
        """
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.db.commit()
            await self.db.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID.

        Args:
            id: Entity UUID

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if instance:
            await self.db.delete(instance)
            await self.db.commit()
            return True
        return False
