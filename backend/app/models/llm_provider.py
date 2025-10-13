"""LLM Provider model for chatbot configuration."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class LLMProviderName(str, Enum):
    """Enum for supported LLM providers."""

    OPENAI = "openai"
    GOOGLE = "google"
    LITELLM = "litellm"
    OLLAMA = "ollama"


class LLMProvider(Base):
    """LLM Provider model for chatbot inference configuration.

    Stores LLM provider configurations for the RAG chatbot. API keys are stored
    in environment variables (.env), not in the database for security.
    """

    __tablename__ = "llm_providers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider_name: Mapped[LLMProviderName] = mapped_column(
        ENUM(
            "openai",
            "google",
            "litellm",
            "ollama",
            name="llm_provider_name",
            create_type=False,
        ),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    api_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    conversations: Mapped[List["Conversation"]] = relationship(
        back_populates="llm_provider"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<LLMProvider(id={self.id}, provider={self.provider_name}, "
            f"model={self.model_name}, default={self.is_default})>"
        )
