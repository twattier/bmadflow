"""Pydantic schemas for LLM Provider API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.llm_provider import LLMProviderName


class LLMProviderCreate(BaseModel):
    """Schema for creating a new LLM provider.

    Example OpenAI:
        {
            "provider_name": "openai",
            "model_name": "gpt-4",
            "is_default": false,
            "api_config": {"temperature": 0.7, "max_tokens": 500}
        }

    Example Ollama:
        {
            "provider_name": "ollama",
            "model_name": "llama3",
            "is_default": true,
            "api_config": {"api_base": "http://localhost:11434"}
        }
    """

    provider_name: LLMProviderName = Field(
        ..., description="LLM provider type (openai, google, litellm, ollama)"
    )
    model_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Model identifier (e.g., gpt-4, llama3, gemini-pro)",
        examples=["gpt-4", "llama3", "gemini-pro", "gpt-3.5-turbo"],
    )
    is_default: bool = Field(
        default=False,
        description="Whether this provider is the default for chat. Only one provider can be default at a time.",
    )
    api_config: Optional[dict] = Field(
        default=None,
        description="Non-sensitive API configuration (e.g., temperature, api_base). API keys go in .env file.",
        examples=[
            {"temperature": 0.7, "max_tokens": 500},
            {"api_base": "http://localhost:11434", "temperature": 0.8},
        ],
    )


class LLMProviderUpdate(BaseModel):
    """Schema for updating an existing LLM provider.

    All fields are optional. Only provided fields will be updated.
    """

    provider_name: Optional[LLMProviderName] = Field(default=None, description="LLM provider type")
    model_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Model identifier",
    )
    is_default: Optional[bool] = Field(
        default=None,
        description="Whether this provider should be the default. Setting this to true will unset other defaults.",
    )
    api_config: Optional[dict] = Field(
        default=None,
        description="Non-sensitive API configuration",
    )


class LLMProviderResponse(BaseModel):
    """Schema for LLM provider API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique provider ID")
    provider_name: LLMProviderName = Field(..., description="LLM provider type")
    model_name: str = Field(..., description="Model identifier")
    is_default: bool = Field(..., description="Whether this is the default provider")
    api_config: Optional[dict] = Field(default=None, description="Non-sensitive API configuration")
    created_at: datetime = Field(..., description="Timestamp when provider was created")
