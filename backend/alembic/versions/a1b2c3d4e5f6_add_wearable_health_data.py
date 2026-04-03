"""add_wearable_health_data

Revision ID: a1b2c3d4e5f6
Revises: 5d51539b24c0
Create Date: 2026-04-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5d51539b24c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('wearable_health_data',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('week_end', sa.Date(), nullable=False),
        sa.Column('avg_heart_rate', sa.Integer()),
        sa.Column('avg_resting_hr', sa.Integer()),
        sa.Column('total_calories', sa.Integer()),
        sa.Column('avg_spo2', sa.Numeric(4, 1)),
        sa.Column('avg_sleep_quality', sa.Integer()),
        sa.Column('avg_sleep_duration_min', sa.Integer()),
        sa.Column('device', sa.String(100)),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_wearable_health_data_user_id', 'wearable_health_data', ['user_id'])
    op.create_unique_constraint('uq_wearable_user_week', 'wearable_health_data', ['user_id', 'week_start'])


def downgrade() -> None:
    op.drop_table('wearable_health_data')
