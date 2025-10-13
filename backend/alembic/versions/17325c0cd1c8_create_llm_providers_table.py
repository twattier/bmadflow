"""create_llm_providers_table

Revision ID: 17325c0cd1c8
Revises: 54bd16acd3ce
Create Date: 2025-10-13 10:01:06.014500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17325c0cd1c8'
down_revision: Union[str, Sequence[str], None] = '54bd16acd3ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ENUM type using raw SQL to avoid double-creation
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE llm_provider_name AS ENUM ('openai', 'google', 'litellm', 'ollama');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create llm_providers table
    op.create_table(
        'llm_providers',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('provider_name', sa.dialects.postgresql.ENUM('openai', 'google', 'litellm', 'ollama', name='llm_provider_name', create_type=False), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('api_config', sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_name', 'model_name', name='uq_provider_model')
    )

    # Create index on is_default for fast lookup
    op.create_index('idx_llm_providers_is_default', 'llm_providers', ['is_default'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('idx_llm_providers_is_default', table_name='llm_providers')

    # Drop table
    op.drop_table('llm_providers')

    # Drop ENUM type
    sa.Enum(name='llm_provider_name').drop(op.get_bind(), checkfirst=True)
