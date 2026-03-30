"""Add HealthMetrics table for smartwatch data storage

Revision ID: 217888fc3501
Revises: 5d51539b24c0
Create Date: 2026-03-30 16:07:08.016927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '217888fc3501'
down_revision: Union[str, Sequence[str], None] = '5d51539b24c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create HealthMetrics table for smartwatch data storage
    op.create_table('health_metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('heart_rate', sa.Integer(), nullable=True),
    sa.Column('calories', sa.Integer(), nullable=True),
    sa.Column('resting_hr', sa.Integer(), nullable=True),
    sa.Column('spo2', sa.Integer(), nullable=True),
    sa.Column('sleep_quality', sa.Integer(), nullable=True),
    sa.Column('steps', sa.Integer(), nullable=True),
    sa.Column('distance', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('active_minutes', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_metrics_date'), 'health_metrics', ['date'], unique=False)
    op.create_index(op.f('ix_health_metrics_id'), 'health_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_health_metrics_user_id'), 'health_metrics', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_health_metrics_user_id'), table_name='health_metrics')
    op.drop_index(op.f('ix_health_metrics_id'), table_name='health_metrics')
    op.drop_index(op.f('ix_health_metrics_date'), table_name='health_metrics')
    op.drop_table('health_metrics')
    # ### end Alembic commands ###
