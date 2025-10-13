"""Conversation model for chatbot sessions."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.llm_provider import LLMProvider
    from app.models.message import Message
    from app.models.project import Project


class Conversation(Base):
    """Conversation model for chatbot sessions.

    Each conversation belongs to a project and uses a specific LLM provider.
    Conversations contain messages and track timestamps for ordering.
    """

    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    llm_provider_id: Mapped[UUID] = mapped_column(ForeignKey("llm_providers.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="conversations")
    llm_provider: Mapped["LLMProvider"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Conversation(id={self.id}, title={self.title}, project_id={self.project_id})>"
