from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Text, Numeric, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base
from enums import UserRole, ExerciseType, ScheduleStatus, AssignmentStatus, SessionStatus, WeekPlanStatus, NotificationType


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20)) # UserRole

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    schedules_as_patient = relationship("Schedule", foreign_keys="[Schedule.patient_id]", back_populates="patient")
    schedules_as_doctor = relationship("Schedule", foreign_keys="[Schedule.doctor_id]", back_populates="doctor")
    assignments_as_patient = relationship("Assignment", foreign_keys="[Assignment.patient_id]", back_populates="patient")
    assignments_as_doctor = relationship("Assignment", foreign_keys="[Assignment.doctor_id]", back_populates="doctor")
    sent_messages = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")
    combos = relationship("Combo", back_populates="doctor")
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    exercise_logs = relationship("ExerciseLogSimple", back_populates="user")
    medical_record = relationship("MedicalRecord", uselist=False, back_populates="patient")
    patient_notes = relationship("PatientNote", foreign_keys="[PatientNote.patient_id]", back_populates="patient")
    doctor_notes = relationship("PatientNote", foreign_keys="[PatientNote.doctor_id]", back_populates="doctor")
    week_plans_as_patient = relationship("WeekPlan", foreign_keys="[WeekPlan.patient_id]", back_populates="patient")
    week_plans_as_doctor = relationship("WeekPlan", foreign_keys="[WeekPlan.doctor_id]", back_populates="doctor")
    notifications = relationship("Notification", back_populates="user")

class ExerciseLogSimple(Base):
    __tablename__ = "exercise_logs_simple"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    date = Column(Date, nullable=False, index=True)
    exercise_type = Column(String(50), nullable=False, index=True)
    feedback = Column(Text)
    rep_count = Column(Integer, default=0, nullable=False)
    session_duration = Column(Numeric(10, 2), default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="exercise_logs")

class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text)
    status = Column(String(20), default=ScheduleStatus.SCHEDULED.value, index=True)

    session_type = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("User", foreign_keys=[patient_id], back_populates="schedules_as_patient")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="schedules_as_doctor")

class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    exercise_type = Column(String(50), nullable=False, index=True)
    target_reps = Column(Integer, default=10)
    frequency = Column(String(50))
    assigned_date = Column(Date, default=func.current_date(), index=True)
    session_time = Column(String(20))
    status = Column(String(20), default=AssignmentStatus.ACTIVE.value, index=True)

    combo_id = Column(Integer, ForeignKey("combos.combo_id"), nullable=True, index=True)
    is_completed = Column(Boolean, default=False)
    duration_seconds = Column(Integer, default=0)
    
    # Week Plan fields
    week_plan_id = Column(Integer, ForeignKey("week_plans.plan_id"), nullable=True)
    day_of_week = Column(Integer, nullable=True) # 1-7
    sets = Column(Integer, default=3)
    rest_seconds = Column(Integer, default=60)
    notes = Column(Text)

    patient = relationship("User", foreign_keys=[patient_id], back_populates="assignments_as_patient")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="assignments_as_doctor")
    combo = relationship("Combo", back_populates="assignments")
    week_plan = relationship("WeekPlan", back_populates="assignments")

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

class Combo(Base):
    __tablename__ = "combos"

    combo_id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor = relationship("User", back_populates="combos")
    items = relationship("ComboItem", back_populates="combo", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="combo")

class ComboItem(Base):
    __tablename__ = "combo_items"

    item_id = Column(Integer, primary_key=True, index=True)
    combo_id = Column(Integer, ForeignKey("combos.combo_id", ondelete="CASCADE"))
    exercise_type = Column(String(50), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    target_reps = Column(Integer, default=10)
    duration_seconds = Column(Integer, default=0)
    instructions = Column(Text)

    combo = relationship("Combo", back_populates="items")

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    plan_id = Column(Integer, nullable=True, index=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    end_time = Column(DateTime(timezone=True))
    status = Column(String(20), default=SessionStatus.IN_PROGRESS.value, index=True)


    user = relationship("User", back_populates="workout_sessions")
    details = relationship("SessionDetail", back_populates="session")

class SessionDetail(Base):
    __tablename__ = "session_details"

    detail_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("workout_sessions.session_id"))
    exercise_type = Column(String(50), nullable=False)
    reps_completed = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    mistakes_count = Column(Integer, default=0)
    accuracy_score = Column(Numeric(5, 2))
    feedback = Column(Text)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())


    session = relationship("WorkoutSession", back_populates="details")

class BrainExerciseLog(Base):
    __tablename__ = "brain_exercise_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    exercise_type = Column(String(50), nullable=False, index=True)
    is_correct = Column(Boolean, nullable=False)
    question_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class BrainExerciseSession(Base):
    __tablename__ = "brain_exercise_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    exercise_type = Column(String(50), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Numeric(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    record_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True)
    diagnosis = Column(Text)
    symptoms = Column(Text)
    treatment_plan = Column(Text)
    height_cm = Column(Numeric(5, 2))
    weight_kg = Column(Numeric(5, 2))
    blood_type = Column(String(5))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    patient = relationship("User", back_populates="medical_record")

class PatientNote(Base):
    __tablename__ = "patient_notes"

    note_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    title = Column(String(200))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_notes")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_notes")

class WeekPlan(Base):
    __tablename__ = "week_plans"

    plan_id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    plan_name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default=WeekPlanStatus.ACTIVE.value, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="week_plans_as_doctor")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="week_plans_as_patient")
    assignments = relationship("Assignment", back_populates="week_plan", cascade="all, delete-orphan")

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    title = Column(String(100))
    message = Column(Text)
    type = Column(String(20), default=NotificationType.INFO.value, index=True)

    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="notifications")
