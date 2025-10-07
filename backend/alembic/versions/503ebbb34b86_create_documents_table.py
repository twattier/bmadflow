"""create documents table

Revision ID: 503ebbb34b86
Revises: 598c0bae7623
Create Date: 2025-10-07 09:18:47.702283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = '503ebbb34b86'
down_revision: Union[str, Sequence[str], None] = '598c0bae7623'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'documents',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_doc_id', UUID(), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['project_doc_id'], ['project_docs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_doc_id', 'file_path', name='uq_project_doc_file_path')
    )
    op.create_index('idx_project_doc_file_path', 'documents', ['project_doc_id', 'file_path'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_project_doc_file_path', table_name='documents')
    op.drop_table('documents')
