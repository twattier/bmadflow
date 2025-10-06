"""Pytest configuration and fixtures for tests."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session.

    Uses the same database as the application. Tests use transactions
    which are committed as normal. Tests should create unique data to avoid conflicts.
    """
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)

    # Create async session factory
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create a session
    async with async_session_factory() as session:
        # Yield the session for the test
        yield session

    # Close the engine
    await engine.dispose()
