"""Add doctor verification workflow fields

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-04-08 21:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('approval_status', sa.String(length=20), nullable=True, server_default='approved'))
    op.create_index('ix_users_approval_status', 'users', ['approval_status'], unique=False)

    op.create_table(
        'doctor_verifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=False, unique=True),
        sa.Column('certificate_url', sa.Text(), nullable=False),
        sa.Column('certificate_public_id', sa.String(length=255), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
    )
    op.create_index('ix_doctor_verifications_id', 'doctor_verifications', ['id'], unique=False)
    op.create_index('ix_doctor_verifications_doctor_id', 'doctor_verifications', ['doctor_id'], unique=True)
    op.create_index('ix_doctor_verifications_reviewed_by', 'doctor_verifications', ['reviewed_by'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_doctor_verifications_reviewed_by', table_name='doctor_verifications')
    op.drop_index('ix_doctor_verifications_doctor_id', table_name='doctor_verifications')
    op.drop_index('ix_doctor_verifications_id', table_name='doctor_verifications')
    op.drop_table('doctor_verifications')

    op.drop_index('ix_users_approval_status', table_name='users')
    op.drop_column('users', 'approval_status')
