"""Pydantic schemas for Conversation API."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""

    llm_provider_id: UUID
    title: Optional[str] = Field(None, max_length=255)


class LLMProviderNested(BaseModel):
    """Nested LLM provider info for conversation responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider_name: str
    model_name: str


class ConversationResponse(BaseModel):
    """Schema for conversation API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    llm_provider_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    llm_provider: Optional[LLMProviderNested] = None


class MessageResponse(BaseModel):
    """Schema for message API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class ConversationWithMessages(BaseModel):
    """Schema for conversation with all messages."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    llm_provider_id: UUID
    title: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime
