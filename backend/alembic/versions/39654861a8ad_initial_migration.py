"""Initial migration

Revision ID: 39654861a8ad
Revises: 
Create Date: 2026-01-10 21:20:27.450450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '39654861a8ad'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('full_name', sa.String(100)),
        sa.Column('role', sa.String(20)),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table('exercise_logs_simple',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('feedback', sa.Text()),
        sa.Column('rep_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('session_duration', sa.Numeric(10, 2), server_default='0.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_exercise_logs_simple_id', 'exercise_logs_simple', ['id'])
    op.create_index('ix_exercise_logs_simple_user_id', 'exercise_logs_simple', ['user_id'])
    op.create_index('ix_exercise_logs_simple_date', 'exercise_logs_simple', ['date'])

    op.create_table('schedules',
        sa.Column('schedule_id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('status', sa.String(20), server_default='scheduled'),
        sa.Column('session_type', sa.String(20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_schedules_schedule_id', 'schedules', ['schedule_id'])

    op.create_table('combos',
        sa.Column('combo_id', sa.Integer(), primary_key=True),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_combos_combo_id', 'combos', ['combo_id'])

    op.create_table('combo_items',
        sa.Column('item_id', sa.Integer(), primary_key=True),
        sa.Column('combo_id', sa.Integer(), sa.ForeignKey('combos.combo_id', ondelete='CASCADE')),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('target_reps', sa.Integer(), server_default='10'),
        sa.Column('duration_seconds', sa.Integer(), server_default='0'),
        sa.Column('instructions', sa.Text()),
    )
    op.create_index('ix_combo_items_item_id', 'combo_items', ['item_id'])

    op.create_table('week_plans',
        sa.Column('plan_id', sa.Integer(), primary_key=True),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('plan_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_week_plans_plan_id', 'week_plans', ['plan_id'])

    op.create_table('assignments',
        sa.Column('assignment_id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('target_reps', sa.Integer(), server_default='10'),
        sa.Column('frequency', sa.String(50)),
        sa.Column('assigned_date', sa.Date(), server_default=sa.text('current_date')),
        sa.Column('session_time', sa.String(20)),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('combo_id', sa.Integer(), sa.ForeignKey('combos.combo_id'), nullable=True),
        sa.Column('is_completed', sa.Boolean(), server_default='false'),
        sa.Column('duration_seconds', sa.Integer(), server_default='0'),
        sa.Column('week_plan_id', sa.Integer(), sa.ForeignKey('week_plans.plan_id'), nullable=True),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('sets', sa.Integer(), server_default='3'),
        sa.Column('rest_seconds', sa.Integer(), server_default='60'),
        sa.Column('notes', sa.Text()),
    )
    op.create_index('ix_assignments_assignment_id', 'assignments', ['assignment_id'])
    op.create_index('ix_assignments_patient_id', 'assignments', ['patient_id'])

    op.create_table('messages',
        sa.Column('message_id', sa.Integer(), primary_key=True),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('receiver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_messages_message_id', 'messages', ['message_id'])

    op.create_table('workout_sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('end_time', sa.DateTime(timezone=True)),
        sa.Column('status', sa.String(20), server_default='in_progress'),
    )

    op.create_table('session_details',
        sa.Column('detail_id', sa.Integer(), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workout_sessions.session_id')),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('reps_completed', sa.Integer(), server_default='0'),
        sa.Column('duration_seconds', sa.Integer(), server_default='0'),
        sa.Column('mistakes_count', sa.Integer(), server_default='0'),
        sa.Column('accuracy_score', sa.Numeric(5, 2)),
        sa.Column('feedback', sa.Text()),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_session_details_detail_id', 'session_details', ['detail_id'])

    op.create_table('brain_exercise_logs',
        sa.Column('log_id', sa.Integer(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('question_number', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_brain_exercise_logs_log_id', 'brain_exercise_logs', ['log_id'])

    op.create_table('brain_exercise_sessions',
        sa.Column('session_id', sa.Integer(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('percentage', sa.Numeric(5, 2)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_brain_exercise_sessions_session_id', 'brain_exercise_sessions', ['session_id'])

    op.create_table('medical_records',
        sa.Column('record_id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id'), unique=True),
        sa.Column('diagnosis', sa.Text()),
        sa.Column('symptoms', sa.Text()),
        sa.Column('treatment_plan', sa.Text()),
        sa.Column('height_cm', sa.Numeric(5, 2)),
        sa.Column('weight_kg', sa.Numeric(5, 2)),
        sa.Column('blood_type', sa.String(5)),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_medical_records_record_id', 'medical_records', ['record_id'])

    op.create_table('patient_notes',
        sa.Column('note_id', sa.Integer(), primary_key=True),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('title', sa.String(200)),
        sa.Column('content', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_patient_notes_note_id', 'patient_notes', ['note_id'])

    op.create_table('notifications',
        sa.Column('notification_id', sa.Integer(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.user_id')),
        sa.Column('title', sa.String(100)),
        sa.Column('message', sa.Text()),
        sa.Column('type', sa.String(20), server_default='info'),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_notifications_notification_id', 'notifications', ['notification_id'])

    op.create_table('otp_verifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('otp_code', sa.String(6), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_data', sa.Text(), nullable=False),
    )
    op.create_index('ix_otp_verifications_email', 'otp_verifications', ['email'])


def downgrade() -> None:
    op.drop_table('otp_verifications')
    op.drop_table('notifications')
    op.drop_table('patient_notes')
    op.drop_table('medical_records')
    op.drop_table('brain_exercise_sessions')
    op.drop_table('brain_exercise_logs')
    op.drop_table('session_details')
    op.drop_table('workout_sessions')
    op.drop_table('messages')
    op.drop_table('assignments')
    op.drop_table('week_plans')
    op.drop_table('combo_items')
    op.drop_table('combos')
    op.drop_table('schedules')
    op.drop_table('exercise_logs_simple')
    op.drop_table('users')
