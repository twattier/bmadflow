"""Pytest configuration and fixtures for tests."""


import pytest_asyncio
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

    # Create async session factory
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create a connection and begin a transaction
    async with engine.connect() as connection:
        # Start a transaction
        transaction = await connection.begin()

        # Create a session bound to this connection
        async with async_session_factory(bind=connection) as session:
            # Mock commit to call flush instead (keeps transaction open)
            original_commit = session.commit

            async def mock_commit():
                await session.flush()

            session.commit = mock_commit

            # Yield the session for the test
            yield session

            # Rollback the transaction after test completes
            await transaction.rollback()

    # Close the engine
    await engine.dispose()
