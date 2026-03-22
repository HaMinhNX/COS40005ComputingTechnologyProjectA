"""remove_unique_fullname

Revision ID: 5d51539b24c0
Revises: simple_status_migration
Create Date: 2026-03-10 04:32:15.920328

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5d51539b24c0'
down_revision: Union[str, Sequence[str], None] = 'simple_status_migration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('users_full_name_unique', 'users', type_='unique')


def downgrade() -> None:
    op.create_unique_constraint('users_full_name_unique', 'users', ['full_name'])
