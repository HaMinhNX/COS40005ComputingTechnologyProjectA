"""add_database_indexes_for_performance

Revision ID: 43bdd7e8a53f
Revises: 39654861a8ad
Create Date: 2026-01-10 21:27:59.266831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43bdd7e8a53f'
down_revision: Union[str, Sequence[str], None] = '39654861a8ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for performance optimization."""
    # Assignments table indexes
    op.create_index('idx_assignment_doctor_id', 'assignments', ['doctor_id'])
    op.create_index('idx_assignment_week_plan_id', 'assignments', ['week_plan_id'])
    op.create_index('idx_assignment_combo_id', 'assignments', ['combo_id'])
    
    # Schedules table indexes
    op.create_index('idx_schedule_doctor_id', 'schedules', ['doctor_id'])
    
    # Messages table indexes
    op.create_index('idx_message_sender_id', 'messages', ['sender_id'])
    op.create_index('idx_message_receiver_id', 'messages', ['receiver_id'])
    op.create_index('idx_message_is_read', 'messages', ['is_read'])
    
    # Combos table indexes
    op.create_index('idx_combo_doctor_id', 'combos', ['doctor_id'])
    
    # Workout sessions table indexes
    op.create_index('idx_workout_session_user_id', 'workout_sessions', ['user_id'])
    op.create_index('idx_workout_session_status', 'workout_sessions', ['status'])
    
    # Session details table indexes
    op.create_index('idx_session_detail_session_id', 'session_details', ['session_id'])
    
    # Brain exercise logs table indexes
    op.create_index('idx_brain_exercise_log_user_id', 'brain_exercise_logs', ['user_id'])
    op.create_index('idx_brain_exercise_log_created_at', 'brain_exercise_logs', ['created_at'])
    
    # Brain exercise sessions table indexes
    op.create_index('idx_brain_exercise_session_user_id', 'brain_exercise_sessions', ['user_id'])
    
    # Medical records table indexes (patient_id already has unique constraint)
    
    # Patient notes table indexes
    op.create_index('idx_patient_note_patient_id', 'patient_notes', ['patient_id'])
    op.create_index('idx_patient_note_doctor_id', 'patient_notes', ['doctor_id'])
    
    # Week plans table indexes
    op.create_index('idx_week_plan_patient_id', 'week_plans', ['patient_id'])
    op.create_index('idx_week_plan_doctor_id', 'week_plans', ['doctor_id'])
    op.create_index('idx_week_plan_status', 'week_plans', ['status'])
    op.create_index('idx_week_plan_dates', 'week_plans', ['start_date', 'end_date'])
    
    # Notifications table indexes
    op.create_index('idx_notification_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notification_is_read', 'notifications', ['is_read'])
    
    # Combo items table indexes
    op.create_index('idx_combo_item_combo_id', 'combo_items', ['combo_id'])


def downgrade() -> None:
    """Remove indexes."""
    # Drop all indexes in reverse order
    op.drop_index('idx_combo_item_combo_id', 'combo_items')
    op.drop_index('idx_notification_is_read', 'notifications')
    op.drop_index('idx_notification_user_id', 'notifications')
    op.drop_index('idx_week_plan_dates', 'week_plans')
    op.drop_index('idx_week_plan_status', 'week_plans')
    op.drop_index('idx_week_plan_doctor_id', 'week_plans')
    op.drop_index('idx_week_plan_patient_id', 'week_plans')
    op.drop_index('idx_patient_note_doctor_id', 'patient_notes')
    op.drop_index('idx_patient_note_patient_id', 'patient_notes')
    op.drop_index('idx_brain_exercise_session_user_id', 'brain_exercise_sessions')
    op.drop_index('idx_brain_exercise_log_created_at', 'brain_exercise_logs')
    op.drop_index('idx_brain_exercise_log_user_id', 'brain_exercise_logs')
    op.drop_index('idx_session_detail_session_id', 'session_details')
    op.drop_index('idx_workout_session_status', 'workout_sessions')
    op.drop_index('idx_workout_session_user_id', 'workout_sessions')
    op.drop_index('idx_combo_doctor_id', 'combos')
    op.drop_index('idx_message_is_read', 'messages')
    op.drop_index('idx_message_receiver_id', 'messages')
    op.drop_index('idx_message_sender_id', 'messages')
    op.drop_index('idx_schedule_doctor_id', 'schedules')
    op.drop_index('idx_assignment_combo_id', 'assignments')
    op.drop_index('idx_assignment_week_plan_id', 'assignments')
    op.drop_index('idx_assignment_doctor_id', 'assignments')

