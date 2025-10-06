"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Create async engine
engine = create_async_engine(settings.database_url, echo=True)

# Create async session factory
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Declarative base for ORM models
Base = declarative_base()


async def get_db():
    """Dependency for route injection."""
    async with AsyncSessionLocal() as session:
        yield session
