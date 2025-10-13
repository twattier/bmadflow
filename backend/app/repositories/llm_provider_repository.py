"""Repository for LLM Provider database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_provider import LLMProvider
from app.schemas.llm_provider import LLMProviderCreate, LLMProviderUpdate


class LLMProviderRepository:
    """Data access layer for LLM Provider operations.

    Handles CRUD operations and enforces business rules:
    - Only one provider can have is_default=True at a time
    - System must always have at least one default provider (AC #6)
    - Cannot delete a default provider
    """

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def _unset_all_defaults(self) -> None:
        """Unset is_default for all providers.

        This is called before setting a new default provider.
        """
        await self.db.execute(
            update(LLMProvider).values(is_default=False).where(LLMProvider.is_default)
        )

    async def get_all(self) -> List[LLMProvider]:
        """Retrieve all LLM providers, ordered by default first, then by creation date.

        Returns:
            List of LLMProvider models ordered by is_default DESC, created_at DESC
        """
        result = await self.db.execute(
            select(LLMProvider).order_by(
                LLMProvider.is_default.desc(), LLMProvider.created_at.desc()
            )
        )
        return list(result.scalars().all())

    async def get_by_id(self, provider_id: UUID) -> Optional[LLMProvider]:
        """Retrieve LLM provider by ID.

        Args:
            provider_id: UUID of the provider

        Returns:
            LLMProvider model or None if not found
        """
        result = await self.db.execute(select(LLMProvider).where(LLMProvider.id == provider_id))
        return result.scalar_one_or_none()

    async def get_default(self) -> Optional[LLMProvider]:
        """Retrieve the default LLM provider.

        Returns:
            LLMProvider model with is_default=True or None if no default exists
        """
        result = await self.db.execute(select(LLMProvider).where(LLMProvider.is_default))
        return result.scalar_one_or_none()

    async def create(self, data: LLMProviderCreate) -> LLMProvider:
        """Create a new LLM provider.

        If is_default=True, automatically unsets all other defaults first.

        Args:
            data: LLMProviderCreate schema with provider details

        Returns:
            Created LLMProvider model
        """
        # If setting as default, unset all other defaults first
        if data.is_default:
            await self._unset_all_defaults()

        provider = LLMProvider(
            provider_name=data.provider_name,
            model_name=data.model_name,
            is_default=data.is_default,
            api_config=data.api_config,
        )

        self.db.add(provider)
        await self.db.flush()
        await self.db.refresh(provider)

        return provider

    async def update(self, provider_id: UUID, data: LLMProviderUpdate) -> Optional[LLMProvider]:
        """Update an existing LLM provider.

        Enforces AC #6: Cannot unset is_default if this is the only/last default provider.

        Args:
            provider_id: UUID of the provider to update
            data: LLMProviderUpdate schema with fields to update

        Returns:
            Updated LLMProvider model or None if not found

        Raises:
            ValueError: If attempting to unset the last default provider
        """
        provider = await self.get_by_id(provider_id)
        if not provider:
            return None

        # Check if attempting to unset the last default (AC #6)
        if data.is_default is False and provider.is_default:
            # Count total providers with is_default=True
            result = await self.db.execute(
                select(LLMProvider).where(LLMProvider.is_default)
            )
            default_count = len(list(result.scalars().all()))

            if default_count <= 1:
                raise ValueError(
                    "Cannot unset default. At least one provider must be marked as default."
                )

        # If setting as default, unset all other defaults first
        if data.is_default is True and not provider.is_default:
            await self._unset_all_defaults()

        # Update fields if provided
        if data.provider_name is not None:
            provider.provider_name = data.provider_name
        if data.model_name is not None:
            provider.model_name = data.model_name
        if data.is_default is not None:
            provider.is_default = data.is_default
        if data.api_config is not None:
            provider.api_config = data.api_config

        await self.db.flush()
        await self.db.refresh(provider)

        return provider

    async def set_default(self, provider_id: UUID) -> Optional[LLMProvider]:
        """Set an LLM provider as the default.

        Automatically unsets all other defaults first.

        Args:
            provider_id: UUID of the provider to set as default

        Returns:
            Updated LLMProvider model or None if not found
        """
        provider = await self.get_by_id(provider_id)
        if not provider:
            return None

        # Unset all other defaults
        await self._unset_all_defaults()

        # Set this provider as default
        provider.is_default = True
        await self.db.flush()
        await self.db.refresh(provider)

        return provider

    async def delete(self, provider_id: UUID) -> bool:
        """Delete an LLM provider.

        Cannot delete a provider if it is the default (AC #6).
        User must set another provider as default first.

        Args:
            provider_id: UUID of the provider to delete

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If attempting to delete a default provider
        """
        provider = await self.get_by_id(provider_id)
        if not provider:
            return False

        if provider.is_default:
            raise ValueError(
                "Cannot delete default provider. Set another provider as default first."
            )

        await self.db.delete(provider)
        await self.db.flush()

        return True
