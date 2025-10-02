"""Relationship model for modeling relationships between documents."""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    text,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from . import Base


class Relationship(Base):
    """Models relationships between documents (epic → story)."""

    __tablename__ = "relationships"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    parent_doc_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    child_doc_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    relationship_type = Column(String(50), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "parent_doc_id",
            "child_doc_id",
            "relationship_type",
            name="unique_parent_child",
        ),
        CheckConstraint("parent_doc_id != child_doc_id", name="no_self_reference"),
    )

    # Relationships
    parent_document = relationship(
        "Document", foreign_keys=[parent_doc_id], back_populates="child_relationships"
    )
    child_document = relationship(
        "Document", foreign_keys=[child_doc_id], back_populates="parent_relationships"
    )
