"""ExtractedEpic model for storing LLM-extracted epic metadata."""

from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from . import Base


class ExtractedEpic(Base):
    """Stores LLM-extracted structured data from epic markdown documents.

    One-to-one relationship with Document via document_id foreign key.
    Populated by EpicExtractionService using OLLAMA LLM inference.
    """

    __tablename__ = "extracted_epics"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title = Column(String(500), nullable=False)
    goal = Column(String, nullable=True)
    status = Column(String(50), nullable=False, server_default=text("'draft'"))
    related_stories = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("NOW()")
    )

    # Relationships
    document = relationship("Document", back_populates="extracted_epic")
