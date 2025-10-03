"""Shared pytest fixtures for all tests."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.models import Base


@pytest_asyncio.fixture
async def db_session():
    """
    Provide a real async database session for integration tests.

    Uses a test database to avoid polluting production data.
    Each test gets a fresh session with auto-rollback.
    """
    # Use test database URL
    DATABASE_URL = "postgresql+asyncpg://bmadflow:bmadflow_dev@localhost:5433/bmadflow"

    # Create async engine for tests
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            # Rollback any changes
            await session.rollback()

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def mock_db():
    """Mock async database session for unit tests that don't need real DB."""
    from unittest.mock import AsyncMock
    return AsyncMock()
