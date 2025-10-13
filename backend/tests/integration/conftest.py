"""Pytest configuration for integration tests."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base


def get_test_database_url():
    """Generate test database URL by replacing database name in production URL.

    This ensures integration tests NEVER touch the production 'bmadflow' database.
    All tests use the separate 'bmadflow_test' database.
    """
    prod_url = settings.database_url
    # Replace only the database name at the END of the URL (after the last /)
    if prod_url.endswith("/bmadflow"):
        return prod_url[:-9] + "/bmadflow_test"
    # Fallback: construct test URL manually
    return "postgresql+asyncpg://bmadflow:changeme_in_production@localhost:5434/bmadflow_test"


# Use environment variable or generate test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", get_test_database_url())


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

    SAFETY: Uses separate TEST database (bmadflow_test) to avoid affecting production data.
    The production 'bmadflow' database is never touched by integration tests.
    """
    # Create async engine using TEST DATABASE
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create session factory
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create all tables (if not exist)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide session
    async with async_session_factory() as session:
        # Track created records for cleanup
        from app.models.conversation import Conversation
        from app.models.document import Document
        from app.models.llm_provider import LLMProvider
        from app.models.message import Message
        from app.models.project import Project
        from app.models.project_doc import ProjectDoc

        # Get initial counts
        initial_project_count = (await session.execute(select(Project))).scalars().all()
        initial_project_ids = {p.id for p in initial_project_count}

        yield session

        # Cleanup: Delete all test data created during the test
        # Delete in order respecting foreign keys:
        # Messages -> Conversations -> Documents -> ProjectDocs -> Projects -> LLMProviders
        await session.execute(delete(Message))
        await session.execute(delete(Conversation))
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

        # Delete LLMProviders created during test (they don't have FK to Project)
        await session.execute(delete(LLMProvider))

        await session.commit()

    # Cleanup
    await engine.dispose()
