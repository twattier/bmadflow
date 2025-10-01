"""Initial schema with projects, documents, relationships

Revision ID: 202510020046
Revises:
Create Date: 2025-10-02 00:46:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '202510020046'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    # Install pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('github_url', sa.String(), nullable=False),
        sa.Column('last_sync_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_status', sa.String(length=50), server_default=sa.text("'idle'"), nullable=False),
        sa.Column('sync_progress', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('doc_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('excerpt', sa.String(), nullable=True),
        sa.Column('last_modified', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('extraction_status', sa.String(length=50), server_default=sa.text("'pending'"), nullable=False),
        sa.Column('extraction_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'file_path', name='unique_project_file')
    )

    # Create indexes on documents table
    op.create_index('idx_documents_project_id', 'documents', ['project_id'])
    op.create_index('idx_documents_doc_type', 'documents', ['doc_type'])
    op.create_index('idx_documents_extraction_status', 'documents', ['extraction_status'])

    # Create relationships table
    op.create_table(
        'relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('parent_doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_doc_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.CheckConstraint('parent_doc_id != child_doc_id', name='no_self_reference'),
        sa.ForeignKeyConstraint(['child_doc_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_doc_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('parent_doc_id', 'child_doc_id', 'relationship_type', name='unique_parent_child')
    )

    # Create indexes on relationships table
    op.create_index('idx_relationships_parent', 'relationships', ['parent_doc_id'])
    op.create_index('idx_relationships_child', 'relationships', ['child_doc_id'])


def downgrade() -> None:
    """Drop database schema in correct order."""
    # Drop tables in reverse order (relationships → documents → projects)
    op.drop_index('idx_relationships_child', table_name='relationships')
    op.drop_index('idx_relationships_parent', table_name='relationships')
    op.drop_table('relationships')

    op.drop_index('idx_documents_extraction_status', table_name='documents')
    op.drop_index('idx_documents_doc_type', table_name='documents')
    op.drop_index('idx_documents_project_id', table_name='documents')
    op.drop_table('documents')

    op.drop_table('projects')

    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
