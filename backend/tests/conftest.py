"""Pytest configuration and fixtures for tests."""

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session with automatic rollback.

    Each test runs in a transaction that is rolled back after the test completes,
    ensuring test isolation and preventing test data accumulation.

    Note: session.commit() is mocked to call flush() instead, preventing
    transaction closure while still updating the session state for tests.
    """
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)

    # Clean up any leftover test data before starting
    async with engine.begin() as conn:
        # Truncate all tables in reverse dependency order to avoid FK violations
        await conn.execute(text("TRUNCATE TABLE chunks CASCADE"))
        await conn.execute(text("TRUNCATE TABLE documents CASCADE"))
        await conn.execute(text("TRUNCATE TABLE project_docs CASCADE"))
        await conn.execute(text("TRUNCATE TABLE projects CASCADE"))

    # Create async session factory
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create a connection and begin a transaction
    async with engine.connect() as connection:
        # Start a transaction
        transaction = await connection.begin()

        # Create a session bound to this connection
        async with async_session_factory(bind=connection) as session:
            # Mock commit to call flush instead (keeps transaction open)
            async def mock_commit():
                await session.flush()

            # Replace the commit method
            session.commit = mock_commit

            # Also ensure savepoint-based transactions work properly
            # by mocking begin_nested to return a context manager that doesn't commit
            original_begin_nested = session.begin_nested

            def mock_begin_nested():
                class MockNested:
                    async def __aenter__(self):
                        return self

                    async def __aexit__(self, *args):
                        pass

                return MockNested()

            session.begin_nested = mock_begin_nested

            # Yield the session for the test
            yield session

            # Rollback the transaction after test completes
            await transaction.rollback()

    # Close the engine
    await engine.dispose()
