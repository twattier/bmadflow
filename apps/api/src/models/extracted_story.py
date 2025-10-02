"""ExtractedStory model for storing LLM-extracted user story components."""

from sqlalchemy import Column, String, DateTime, Float, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from . import Base


class ExtractedStory(Base):
    """Stores LLM-extracted structured data from story markdown documents.

    One-to-one relationship with Document via document_id foreign key.
    Populated by StoryExtractionService using OLLAMA LLM inference.
    """

    __tablename__ = "extracted_stories"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    role = Column(String(500), nullable=True)
    action = Column(String(1000), nullable=True)
    benefit = Column(String(1000), nullable=True)
    acceptance_criteria = Column(JSONB, nullable=True)
    status = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
    )

    # Relationships
    document = relationship("Document", backref="extracted_story")
