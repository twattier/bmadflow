"""enable_pgvector

Revision ID: 4f955bd4b68d
Revises: 503ebbb34b86
Create Date: 2025-10-10 00:07:26.743906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f955bd4b68d'
down_revision: Union[str, Sequence[str], None] = '503ebbb34b86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable pgvector extension for vector embeddings."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    """Disable pgvector extension."""
    op.execute("DROP EXTENSION IF EXISTS vector;")
