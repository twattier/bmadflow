"""ProjectDoc SQLAlchemy model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.project import Project


class ProjectDoc(Base):
    """ProjectDoc model for linking GitHub repositories to projects."""

    __tablename__ = "project_docs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    github_url: Mapped[str] = mapped_column(String(512), nullable=False)
    github_folder_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_github_commit_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
    project: Mapped["Project"] = relationship("Project", back_populates="project_docs")
    documents: Mapped[List["Document"]] = relationship(
        "Document", back_populates="project_doc", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return string representation of ProjectDoc."""
        return f"<ProjectDoc(id={self.id}, name={self.name}, project_id={self.project_id})>"
