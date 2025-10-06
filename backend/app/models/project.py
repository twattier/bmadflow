"""Project model for organizing BMAD documentation."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    pass


class Project(Base):
    """Project model for organizing documentation initiatives."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship (will be added in Story 2.2 when ProjectDoc model is created)
    # project_docs: Mapped[List["ProjectDoc"]] = relationship(
    #     "ProjectDoc", back_populates="project", cascade="all, delete-orphan"
    # )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Project(id={self.id}, name={self.name})>"
