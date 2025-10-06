"""create_projects_table

Revision ID: e43b4d239b48
Revises: 913c62af99ce
Create Date: 2025-10-07 01:03:41.046895

Creates the projects table for organizing BMAD documentation by initiative.

This table is the foundation for Epic 2 (Project & Documentation Management).
Each project can have multiple ProjectDocs, which link to GitHub repositories.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'e43b4d239b48'
down_revision: Union[str, Sequence[str], None] = '913c62af99ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create projects table."""
    # Enable uuid-ossp extension if not already enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    """Drop projects table."""
    op.drop_table('projects')
    # Note: Not dropping uuid-ossp extension as it may be used by other tables
