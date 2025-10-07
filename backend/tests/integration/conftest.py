"""Pytest configuration for integration tests."""

import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide async database session with automatic cleanup after test.

    Uses real database connection and cleans up all test data after each test.
    """
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)

    # Create session factory
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create all tables (if not exist)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide session
    async with async_session_factory() as session:
        # Track created records for cleanup
        from app.models.document import Document
        from app.models.project import Project
        from app.models.project_doc import ProjectDoc

        # Get initial counts
        initial_project_count = (await session.execute(select(Project))).scalars().all()
        initial_project_ids = {p.id for p in initial_project_count}

        yield session

        # Cleanup: Delete all test data created during the test
        # Delete in order: Documents -> ProjectDocs -> Projects
        await session.execute(delete(Document))

        # Delete ProjectDocs created during test
        result = await session.execute(select(ProjectDoc))
        for pd in result.scalars().all():
            if pd.project_id not in initial_project_ids:
                await session.delete(pd)

        # Delete Projects created during test
        result = await session.execute(select(Project))
        for p in result.scalars().all():
            if p.id not in initial_project_ids:
                await session.delete(p)

        await session.commit()

    # Cleanup
    await engine.dispose()
