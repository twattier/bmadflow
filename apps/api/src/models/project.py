"""Project model for storing GitHub repository sync metadata."""

from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from . import Base


class Project(Base):
    """Represents a GitHub repository project synced into BMADFlow."""

    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name = Column(String(255), nullable=False)
    github_url = Column(String, nullable=False)
    last_sync_timestamp = Column(DateTime(timezone=True), nullable=True)
    sync_status = Column(String(50), nullable=False, server_default=text("'idle'"))
    sync_progress = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    documents = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan"
    )
