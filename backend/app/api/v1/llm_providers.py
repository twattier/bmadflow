"""API endpoints for LLM Provider management."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.llm_provider_repository import LLMProviderRepository
from app.schemas.llm_provider import (
    LLMProviderCreate,
    LLMProviderResponse,
    LLMProviderUpdate,
)

router = APIRouter(prefix="/api/llm-providers", tags=["llm-providers"])


def get_llm_provider_repository(db: AsyncSession = Depends(get_db)) -> LLMProviderRepository:
    """Dependency injection for LLMProviderRepository.

    Args:
        db: Database session from dependency

    Returns:
        LLMProviderRepository instance
    """
    return LLMProviderRepository(db)


@router.post(
    "/",
    response_model=LLMProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create LLM Provider",
    description="""
Create a new LLM provider configuration.

**API Keys**: Store API keys in `.env` file, not in `api_config`.

**Default Provider**: If `is_default=true`, all other providers will be automatically set to `false`.

**Examples**:
- **OpenAI**: `{"provider_name": "openai", "model_name": "gpt-4", "api_config": {"temperature": 0.7}}`
- **Google**: `{"provider_name": "google", "model_name": "gemini-pro", "api_config": {"temperature": 0.8}}`
- **LiteLLM**: `{"provider_name": "litellm", "model_name": "gpt-3.5-turbo", "api_config": {"max_tokens": 500}}`
- **Ollama**: `{"provider_name": "ollama", "model_name": "llama3", "is_default": true, "api_config": {"api_base": "http://localhost:11434"}}`
    """,
)
async def create_llm_provider(
    data: LLMProviderCreate,
    repo: LLMProviderRepository = Depends(get_llm_provider_repository),
    db: AsyncSession = Depends(get_db),
) -> LLMProviderResponse:
    """Create a new LLM provider."""
    try:
        async with db.begin():
            provider = await repo.create(data)
            return LLMProviderResponse.model_validate(provider)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create provider: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[LLMProviderResponse],
    summary="List LLM Providers",
    description="Retrieve all LLM provider configurations. Results are ordered with default provider first, then by creation date.",
)
async def list_llm_providers(
    repo: LLMProviderRepository = Depends(get_llm_provider_repository),
) -> List[LLMProviderResponse]:
    """List all LLM providers."""
    providers = await repo.get_all()
    return [LLMProviderResponse.model_validate(p) for p in providers]


@router.get(
    "/{provider_id}",
    response_model=LLMProviderResponse,
    summary="Get LLM Provider",
    description="Retrieve a specific LLM provider by ID.",
)
async def get_llm_provider(
    provider_id: UUID,
    repo: LLMProviderRepository = Depends(get_llm_provider_repository),
) -> LLMProviderResponse:
    """Get a specific LLM provider by ID."""
    provider = await repo.get_by_id(provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LLM provider {provider_id} not found",
        )
    return LLMProviderResponse.model_validate(provider)


@router.put(
    "/{provider_id}",
    response_model=LLMProviderResponse,
    summary="Update LLM Provider",
    description="""
Update an existing LLM provider configuration.

**Important**: Cannot set `is_default=false` if this is the only default provider.
The system must always have at least one default provider.
    """,
)
async def update_llm_provider(
    provider_id: UUID,
    data: LLMProviderUpdate,
    repo: LLMProviderRepository = Depends(get_llm_provider_repository),
    db: AsyncSession = Depends(get_db),
) -> LLMProviderResponse:
    """Update an LLM provider."""
    try:
        async with db.begin():
            provider = await repo.update(provider_id, data)
            if not provider:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LLM provider {provider_id} not found",
                )
            return LLMProviderResponse.model_validate(provider)
    except ValueError as e:
        # AC #6: Cannot unset last default
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update provider: {str(e)}",
        )


@router.put(
    "/{provider_id}/set-default",
    response_model=LLMProviderResponse,
    summary="Set Default Provider",
    description="Set an LLM provider as the default for chat. All other providers will be automatically set to non-default.",
)
async def set_default_provider(
    provider_id: UUID,
    repo: LLMProviderRepository = Depends(get_llm_provider_repository),
    db: AsyncSession = Depends(get_db),
) -> LLMProviderResponse:
    """Set an LLM provider as the default."""
    async with db.begin():
        provider = await repo.set_default(provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LLM provider {provider_id} not found",
            )
        return LLMProviderResponse.model_validate(provider)


@router.delete(
    "/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete LLM Provider",
    description="""
Delete an LLM provider.

**Important**: Cannot delete a default provider. Set another provider as default first.
    """,
)
async def delete_llm_provider(
    provider_id: UUID,
    repo: LLMProviderRepository = Depends(get_llm_provider_repository),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an LLM provider."""
    try:
        async with db.begin():
            deleted = await repo.delete(provider_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LLM provider {provider_id} not found",
                )
    except ValueError as e:
        # Cannot delete default provider
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
