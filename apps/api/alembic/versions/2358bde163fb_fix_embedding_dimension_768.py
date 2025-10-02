"""fix_embedding_dimension_768

Revision ID: 2358bde163fb
Revises: 202510020046
Create Date: 2025-10-03 00:10:50.956768

Fixes embedding dimension from 384 to 768 to match nomic-embed-text model output.
Model info confirms: "nomic-bert.embedding_length":768
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2358bde163fb'
down_revision: Union[str, Sequence[str], None] = '202510020046'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Change embedding column from vector(384) to vector(768)."""
    # Alter the embedding column type
    op.execute('ALTER TABLE documents ALTER COLUMN embedding TYPE vector(768)')


def downgrade() -> None:
    """Downgrade schema: Revert embedding column to vector(384)."""
    op.execute('ALTER TABLE documents ALTER COLUMN embedding TYPE vector(384)')
