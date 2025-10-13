"""Unit tests for LLM Provider Repository."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_provider import LLMProvider, LLMProviderName
from app.repositories.llm_provider_repository import LLMProviderRepository
from app.schemas.llm_provider import LLMProviderCreate, LLMProviderUpdate


@pytest.fixture
async def repo(db_session: AsyncSession) -> LLMProviderRepository:
    """Create repository instance with test database session."""
    return LLMProviderRepository(db_session)


@pytest.fixture
async def sample_provider(db_session: AsyncSession) -> LLMProvider:
    """Create a sample LLM provider for testing."""
    provider = LLMProvider(
        provider_name=LLMProviderName.OLLAMA,
        model_name="llama3",
        is_default=True,
        api_config={"api_base": "http://localhost:11434"},
    )
    db_session.add(provider)
    await db_session.flush()
    await db_session.refresh(provider)
    return provider


@pytest.mark.asyncio
class TestLLMProviderRepository:
    """Test suite for LLMProviderRepository."""

    async def test_create_provider(
        self, repo: LLMProviderRepository, db_session: AsyncSession
    ):
        """Test creating a new LLM provider."""
        data = LLMProviderCreate(
            provider_name=LLMProviderName.OPENAI,
            model_name="gpt-4",
            is_default=False,
            api_config={"temperature": 0.7},
        )

        provider = await repo.create(data)

        assert provider.id is not None
        assert provider.provider_name == LLMProviderName.OPENAI
        assert provider.model_name == "gpt-4"
        assert provider.is_default is False
        assert provider.api_config == {"temperature": 0.7}
        assert provider.created_at is not None

    async def test_create_with_is_default_unsets_others(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider, db_session: AsyncSession
    ):
        """Test that creating a provider with is_default=True unsets all others."""
        # sample_provider is already default
        assert sample_provider.is_default is True

        # Create new provider as default
        data = LLMProviderCreate(
            provider_name=LLMProviderName.OPENAI,
            model_name="gpt-4",
            is_default=True,
            api_config={},
        )

        new_provider = await repo.create(data)
        await db_session.refresh(sample_provider)

        # New provider should be default
        assert new_provider.is_default is True

        # Old provider should no longer be default
        assert sample_provider.is_default is False

    async def test_get_all_orders_by_default_first(
        self, repo: LLMProviderRepository, db_session: AsyncSession
    ):
        """Test that get_all returns providers with default first."""
        # Create non-default provider
        provider1 = LLMProvider(
            provider_name=LLMProviderName.OPENAI,
            model_name="gpt-4",
            is_default=False,
        )
        db_session.add(provider1)

        # Create default provider
        provider2 = LLMProvider(
            provider_name=LLMProviderName.OLLAMA,
            model_name="llama3",
            is_default=True,
        )
        db_session.add(provider2)
        await db_session.flush()

        providers = await repo.get_all()

        assert len(providers) == 2
        # Default should be first
        assert providers[0].is_default is True
        assert providers[0].id == provider2.id
        assert providers[1].is_default is False
        assert providers[1].id == provider1.id

    async def test_get_by_id_returns_provider(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider
    ):
        """Test getting a provider by ID returns the correct provider."""
        provider = await repo.get_by_id(sample_provider.id)

        assert provider is not None
        assert provider.id == sample_provider.id
        assert provider.provider_name == sample_provider.provider_name
        assert provider.model_name == sample_provider.model_name

    async def test_get_by_id_returns_none_when_not_found(self, repo: LLMProviderRepository):
        """Test getting a provider by ID returns None when not found."""
        provider = await repo.get_by_id(uuid4())

        assert provider is None

    async def test_get_default_returns_default_provider(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider
    ):
        """Test getting the default provider."""
        provider = await repo.get_default()

        assert provider is not None
        assert provider.is_default is True
        assert provider.id == sample_provider.id

    async def test_get_default_returns_none_when_no_default(
        self, repo: LLMProviderRepository, db_session: AsyncSession
    ):
        """Test getting default provider when none exist."""
        provider = await repo.get_default()

        assert provider is None

    async def test_update_provider(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider
    ):
        """Test updating a provider's fields."""
        data = LLMProviderUpdate(
            model_name="llama3.1",
            api_config={"api_base": "http://localhost:11435", "temperature": 0.8},
        )

        updated = await repo.update(sample_provider.id, data)

        assert updated is not None
        assert updated.model_name == "llama3.1"
        assert updated.api_config == {
            "api_base": "http://localhost:11435",
            "temperature": 0.8,
        }
        # is_default should remain unchanged
        assert updated.is_default is True

    async def test_update_prevents_unsetting_last_default(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider
    ):
        """Test that updating the only default provider to is_default=False raises error (AC #6)."""
        data = LLMProviderUpdate(is_default=False)

        with pytest.raises(ValueError, match="Cannot unset default"):
            await repo.update(sample_provider.id, data)

    async def test_update_allows_unsetting_default_when_others_exist(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider, db_session: AsyncSession
    ):
        """Test that unsetting default is allowed when other default providers exist."""
        # Create another default provider
        provider2 = LLMProvider(
            provider_name=LLMProviderName.OPENAI,
            model_name="gpt-4",
            is_default=True,
        )
        db_session.add(provider2)
        await db_session.flush()

        # Now unset the first default (should work)
        data = LLMProviderUpdate(is_default=False)
        updated = await repo.update(sample_provider.id, data)

        assert updated is not None
        assert updated.is_default is False

    async def test_set_default_unsets_others(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider, db_session: AsyncSession
    ):
        """Test that set_default unsets all other defaults."""
        # Create another provider (not default)
        provider2 = LLMProvider(
            provider_name=LLMProviderName.OPENAI,
            model_name="gpt-4",
            is_default=False,
        )
        db_session.add(provider2)
        await db_session.flush()
        await db_session.refresh(provider2)

        # Set provider2 as default
        updated = await repo.set_default(provider2.id)
        await db_session.refresh(sample_provider)

        assert updated is not None
        assert updated.is_default is True
        assert sample_provider.is_default is False

    async def test_set_default_returns_none_when_not_found(self, repo: LLMProviderRepository):
        """Test set_default returns None when provider not found."""
        result = await repo.set_default(uuid4())

        assert result is None

    async def test_delete_non_default_provider(
        self, repo: LLMProviderRepository, db_session: AsyncSession
    ):
        """Test deleting a non-default provider."""
        provider = LLMProvider(
            provider_name=LLMProviderName.OPENAI,
            model_name="gpt-4",
            is_default=False,
        )
        db_session.add(provider)
        await db_session.flush()
        await db_session.refresh(provider)

        deleted = await repo.delete(provider.id)

        assert deleted is True

        # Verify it's gone
        result = await db_session.execute(
            select(LLMProvider).where(LLMProvider.id == provider.id)
        )
        assert result.scalar_one_or_none() is None

    async def test_delete_default_provider_raises_error(
        self, repo: LLMProviderRepository, sample_provider: LLMProvider
    ):
        """Test that deleting a default provider raises an error."""
        with pytest.raises(ValueError, match="Cannot delete default provider"):
            await repo.delete(sample_provider.id)

    async def test_delete_returns_false_when_not_found(self, repo: LLMProviderRepository):
        """Test delete returns False when provider not found."""
        deleted = await repo.delete(uuid4())

        assert deleted is False
