"""create_project_docs_table

Revision ID: 598c0bae7623
Revises: e43b4d239b48
Create Date: 2025-10-07 01:23:04.122990

Creates the project_docs table for linking GitHub repositories to projects.
This table stores configuration for syncing documentation from GitHub repos.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '598c0bae7623'
down_revision: Union[str, Sequence[str], None] = 'e43b4d239b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create project_docs table."""
    op.create_table(
        'project_docs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('github_url', sa.String(512), nullable=False),
        sa.Column('github_folder_path', sa.String(512), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_github_commit_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Drop project_docs table."""
    op.drop_table('project_docs')
