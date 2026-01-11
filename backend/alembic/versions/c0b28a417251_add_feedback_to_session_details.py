"""add feedback to session_details

Revision ID: c0b28a417251
Revises: 43bdd7e8a53f
Create Date: 2026-01-11 09:09:39.151817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0b28a417251'
down_revision: Union[str, Sequence[str], None] = '43bdd7e8a53f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('session_details', sa.Column('feedback', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('session_details', 'feedback')

