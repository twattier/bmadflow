"""Document model for storing markdown files from GitHub repos."""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Float,
    ForeignKey,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from . import Base


class Document(Base):
    """Represents a single markdown file from a GitHub repository."""

    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path = Column(String, nullable=False)
    content = Column(String, nullable=False)
    doc_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    excerpt = Column(String, nullable=True)
    last_modified = Column(DateTime(timezone=True), nullable=True)
    embedding = Column(Vector(384), nullable=True)
    extraction_status = Column(
        String(50), nullable=False, server_default=text("'pending'")
    )
    extraction_confidence = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("project_id", "file_path", name="unique_project_file"),
    )

    # Relationships
    project = relationship("Project", back_populates="documents")
    parent_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.child_doc_id",
        back_populates="child_document",
        cascade="all, delete-orphan",
    )
    child_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.parent_doc_id",
        back_populates="parent_document",
        cascade="all, delete-orphan",
    )
