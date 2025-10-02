"""create_extraction_tables

Revision ID: f33a8da5c6eb
Revises: 2358bde163fb
Create Date: 2025-10-03 00:26:19.354564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = 'f33a8da5c6eb'
down_revision: Union[str, Sequence[str], None] = '2358bde163fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Create extracted_stories and extracted_epics tables."""

    # Create extracted_stories table
    op.create_table(
        'extracted_stories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('role', sa.String(500), nullable=True),
        sa.Column('action', sa.String(1000), nullable=True),
        sa.Column('benefit', sa.String(1000), nullable=True),
        sa.Column('acceptance_criteria', JSONB, nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # Create extracted_epics table
    op.create_table(
        'extracted_epics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('goal', sa.String, nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('related_stories', JSONB, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # Create indexes for common queries
    op.create_index('idx_extracted_stories_status', 'extracted_stories', ['status'])
    op.create_index('idx_extracted_epics_status', 'extracted_epics', ['status'])


def downgrade() -> None:
    """Downgrade schema: Drop extracted_stories and extracted_epics tables."""
    op.drop_index('idx_extracted_epics_status')
    op.drop_index('idx_extracted_stories_status')
    op.drop_table('extracted_epics')
    op.drop_table('extracted_stories')
