"""
Schema package initialization.
Exports all schemas for easy importing.
"""
from schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserWithToken,
    UserListItem,
    PatientCreate,
    PatientResponse,
    DoctorResponse,
)

from schemas.exercise import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    ComboItemCreate,
    ComboItemResponse,
    ComboCreate,
    ComboUpdate,
    ComboResponse,
    SessionDetailCreate,
    SessionDetailResponse,
    WorkoutSessionCreate,
    WorkoutSessionEnd,
    WorkoutSessionResponse,
    ExerciseLogCreate,
    ExerciseLogResponse,
    WeekPlanCreate,
    WeekPlanUpdate,
    WeekPlanResponse,
    OverallStatsResponse,
    WeeklyProgressResponse,
)

from schemas.medical import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
    PatientNoteCreate,
    PatientNoteUpdate,
    PatientNoteResponse,
)

from schemas.communication import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserWithToken",
    "UserListItem",
    "PatientCreate",
    "PatientResponse",
    "DoctorResponse",
    # Exercise schemas
    "AssignmentCreate",
    "AssignmentUpdate",
    "AssignmentResponse",
    "ComboItemCreate",
    "ComboItemResponse",
    "ComboCreate",
    "ComboUpdate",
    "ComboResponse",
    "SessionDetailCreate",
    "SessionDetailResponse",
    "WorkoutSessionCreate",
    "WorkoutSessionEnd",
    "WorkoutSessionResponse",
    "ExerciseLogCreate",
    "ExerciseLogResponse",
    "WeekPlanCreate",
    "WeekPlanUpdate",
    "WeekPlanResponse",
    "OverallStatsResponse",
    "WeeklyProgressResponse",
    # Medical schemas
    "MedicalRecordCreate",
    "MedicalRecordUpdate",
    "MedicalRecordResponse",
    "PatientNoteCreate",
    "PatientNoteUpdate",
    "PatientNoteResponse",
    # Communication schemas
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "MessageCreate",
    "MessageUpdate",
    "MessageResponse",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
]
