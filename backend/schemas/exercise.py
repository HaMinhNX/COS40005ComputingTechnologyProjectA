"""
Pydantic schemas for Exercise and Workout-related operations.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enums import ExerciseType, SessionStatus


# ============ Exercise Assignment Schemas ============

class AssignmentCreate(BaseModel):
    """Schema for creating an exercise assignment"""
    patient_id: UUID
    exercise_type: Optional[ExerciseType] = None

    target_reps: int = Field(default=10, ge=0, le=1000)
    frequency: Optional[str] = Field(None, max_length=50)
    session_time: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    combo_id: Optional[int] = None
    week_plan_id: Optional[int] = None
    day_of_week: Optional[int] = Field(None, ge=1, le=7)
    sets: int = Field(default=3, ge=1, le=10)
    rest_seconds: int = Field(default=60, ge=0, le=600)
    duration_seconds: int = Field(default=0, ge=0)


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment"""
    target_reps: Optional[int] = Field(None, ge=1, le=1000)
    frequency: Optional[str] = Field(None, max_length=50)
    session_time: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    is_completed: Optional[bool] = None


class AssignmentResponse(BaseModel):
    """Schema for assignment response"""
    assignment_id: int
    patient_id: UUID
    doctor_id: UUID
    exercise_type: str
    target_reps: int
    frequency: Optional[str]
    assigned_date: date
    session_time: Optional[str]
    status: str
    is_completed: bool
    duration_seconds: int
    combo_id: Optional[int]
    week_plan_id: Optional[int]
    day_of_week: Optional[int]
    sets: int
    rest_seconds: int
    notes: Optional[str]

    class Config:
        from_attributes = True


# ============ Combo Schemas ============

class ComboItemCreate(BaseModel):
    """Schema for creating a combo item"""
    exercise_type: ExerciseType
    sequence_order: int = Field(..., ge=1)
    target_reps: int = Field(default=10, ge=1, le=1000)
    duration_seconds: int = Field(default=0, ge=0)
    instructions: Optional[str] = None


class ComboItemResponse(BaseModel):
    """Schema for combo item response"""
    item_id: int
    combo_id: int
    exercise_type: str
    sequence_order: int
    target_reps: int
    duration_seconds: int
    instructions: Optional[str]

    class Config:
        from_attributes = True


class ComboCreate(BaseModel):
    """Schema for creating a combo"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    items: List[ComboItemCreate] = Field(..., min_items=1)


class ComboUpdate(BaseModel):
    """Schema for updating a combo"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class ComboResponse(BaseModel):
    """Schema for combo response"""
    combo_id: int
    doctor_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    items: List[ComboItemResponse] = []

    class Config:
        from_attributes = True


# ============ Workout Session Schemas ============

class SessionDetailCreate(BaseModel):
    """Schema for creating a session detail"""
    exercise_type: ExerciseType
    reps_completed: int = Field(default=0, ge=0)
    duration_seconds: int = Field(default=0, ge=0)
    mistakes_count: int = Field(default=0, ge=0)
    accuracy_score: Optional[Decimal] = Field(None, ge=0, le=100)
    feedback: Optional[str] = None



class SessionDetailResponse(BaseModel):
    """Schema for session detail response"""
    detail_id: int
    session_id: UUID
    exercise_type: str
    reps_completed: int
    duration_seconds: int
    mistakes_count: int
    accuracy_score: Optional[Decimal]
    feedback: Optional[str]
    completed_at: datetime


    class Config:
        from_attributes = True


class WorkoutSessionCreate(BaseModel):
    """Schema for creating a workout session"""
    plan_id: Optional[int] = None


class WorkoutSessionEnd(BaseModel):
    """Schema for ending a workout session"""
    session_id: UUID


class WorkoutSessionResponse(BaseModel):
    """Schema for workout session response"""
    session_id: UUID
    user_id: UUID
    plan_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    details: List[SessionDetailResponse] = []

    class Config:
        from_attributes = True


# ============ Exercise Log Schemas (Legacy - to be deprecated) ============

class ExerciseLogCreate(BaseModel):
    """Schema for creating an exercise log (legacy)"""
    exercise_type: ExerciseType
    feedback: Optional[str] = None
    rep_count: int = Field(default=0, ge=0)
    session_duration: Decimal = Field(default=0.0, ge=0)


class ExerciseLogResponse(BaseModel):
    """Schema for exercise log response (legacy)"""
    id: int
    user_id: UUID
    date: date
    exercise_type: str
    feedback: Optional[str]
    rep_count: int
    session_duration: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Week Plan Schemas ============

class WeekPlanCreate(BaseModel):
    """Schema for creating a week plan"""
    patient_id: UUID
    plan_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: date
    end_date: date
    exercises: List[AssignmentCreate] = Field(..., min_items=1)

    @validator('end_date')
    def validate_dates(cls, v, values):
        """Ensure end_date is after start_date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class WeekPlanUpdate(BaseModel):
    """Schema for updating a week plan"""
    plan_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)


class WeekPlanResponse(BaseModel):
    """Schema for week plan response"""
    plan_id: int
    doctor_id: UUID
    patient_id: UUID
    plan_name: str
    description: Optional[str]
    start_date: date
    end_date: date
    status: str
    created_at: datetime
    updated_at: datetime
    assignments: List[AssignmentResponse] = []

    class Config:
        from_attributes = True


# ============ Statistics Schemas ============

class OverallStatsResponse(BaseModel):
    """Schema for overall statistics response"""
    total_reps: int
    total_sessions: int
    total_duration_minutes: float
    streak_days: int
    exercises_completed: dict


class WeeklyProgressResponse(BaseModel):
    """Schema for weekly progress response"""
    week_data: List[dict]
    total_reps_this_week: int
    completion_rate: float
# ============ Camera Processing Schemas ============

class LandmarkData(BaseModel):
    """Schema for a single MediaPipe landmark"""
    x: float
    y: float
    z: float = 0.0
    visibility: float = 0.0


class ProcessRequest(BaseModel):
    """Schema for landmark processing request"""
    landmarks: List[LandmarkData]
    current_exercise: str
    user_id: Optional[str] = None


class ProcessResponse(BaseModel):
    """Schema for landmark processing response"""
    squat_count: int
    curl_count: int
    shoulder_flexion_count: int
    knee_raise_count: int
    total_reps: int
    squat_state_name: str
    curl_state_name: str
    shoulder_flexion_state_name: str
    knee_raise_state_name: str
    feedback: str
