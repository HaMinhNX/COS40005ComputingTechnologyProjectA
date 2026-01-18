"""add_user_status_columns

Revision ID: simple_status_migration
Revises: c0b28a417251
Create Date: 2026-01-17 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'simple_status_migration'
down_revision: Union[str, Sequence[str], None] = 'c0b28a417251'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add last_active_at and status columns to users table."""
    # Add columns if they don't exist
    op.add_column('users', sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('status', sa.String(length=20), nullable=True, server_default='active'))


def downgrade() -> None:
    """Remove the new columns."""
    op.drop_column('users', 'status')
    op.drop_column('users', 'last_active_at')
