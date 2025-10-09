"""create_chunks_table

Revision ID: 54bd16acd3ce
Revises: 4f955bd4b68d
Create Date: 2025-10-10 00:08:23.080931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '54bd16acd3ce'
down_revision: Union[str, Sequence[str], None] = '4f955bd4b68d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chunks table with pgvector support."""
    # Create chunks table
    op.create_table(
        'chunks',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('document_id', UUID(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=False),
        sa.Column('header_anchor', sa.String(512), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE')
    )

    # Create composite index for ordered chunk retrieval
    op.create_index('idx_document_chunk', 'chunks', ['document_id', 'chunk_index'])

    # Create index on document_id for fast document-scoped queries
    op.create_index('idx_chunks_document_id', 'chunks', ['document_id'])

    # Create HNSW vector index for similarity search (performance target: <500ms)
    # Parameters: m=16 (max connections per layer), ef_construction=64 (build-time candidate list)
    op.execute("""
        CREATE INDEX chunks_embedding_idx ON chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)


def downgrade() -> None:
    """Drop chunks table and all indexes."""
    op.drop_index('chunks_embedding_idx', table_name='chunks')
    op.drop_index('idx_chunks_document_id', table_name='chunks')
    op.drop_index('idx_document_chunk', table_name='chunks')
    op.drop_table('chunks')
