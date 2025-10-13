"""Add conversations and messages tables

Revision ID: f1fc103cd71d
Revises: 17325c0cd1c8
Create Date: 2025-10-13 12:12:29.161898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1fc103cd71d'
down_revision: Union[str, Sequence[str], None] = '17325c0cd1c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create conversations table
    op.create_table('conversations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('project_id', sa.Uuid(), nullable=False),
    sa.Column('llm_provider_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['llm_provider_id'], ['llm_providers.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # Create index on conversations for efficient querying by project
    op.create_index('idx_conversations_project_updated', 'conversations', ['project_id', sa.text('updated_at DESC')])

    # Create messages table
    op.create_table('messages',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('conversation_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("role IN ('user', 'assistant')", name='ck_message_role'),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # Create index on messages for efficient querying by conversation
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', sa.text('created_at ASC')])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('idx_conversations_project_updated', table_name='conversations')

    # Drop tables (messages first due to FK dependency)
    op.drop_table('messages')
    op.drop_table('conversations')
