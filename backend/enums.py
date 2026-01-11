"""
Enums for the application to replace magic strings and improve type safety.
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""
    DOCTOR = "doctor"
    PATIENT = "patient"


class ExerciseType(str, Enum):
    """Available exercise types"""
    BICEP_CURL = "bicep-curl"
    SHOULDER_FLEXION = "shoulder-flexion"
    SQUAT = "squat"
    KNEE_RAISE = "knee-raise"


class ScheduleStatus(str, Enum):
    """Status of scheduled appointments"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class AssignmentStatus(str, Enum):
    """Status of exercise assignments"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SessionStatus(str, Enum):
    """Status of workout sessions"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class WeekPlanStatus(str, Enum):
    """Status of weekly workout plans"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DRAFT = "draft"


class NotificationType(str, Enum):
    """Types of notifications"""
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"
    REMINDER = "reminder"


class SessionType(str, Enum):
    """Types of scheduled sessions"""
    CONSULTATION = "consultation"
    CHECKUP = "checkup"
    THERAPY = "therapy"
    FOLLOWUP = "followup"


# Daily target reps for each exercise type
DAILY_TARGETS = {
    ExerciseType.BICEP_CURL: 10,
    ExerciseType.SHOULDER_FLEXION: 10,
    ExerciseType.SQUAT: 10,
    ExerciseType.KNEE_RAISE: 10,
}
