"""
Pydantic schemas for Schedules and Messages.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enums import ScheduleStatus, SessionType


# ============ Schedule Schemas ============

class ScheduleCreate(BaseModel):
    """Schema for creating a schedule"""
    patient_id: UUID
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None
    session_type: Optional[SessionType] = None

    @validator('end_time')
    def validate_times(cls, v, values):
        """Ensure end_time is after start_time"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[ScheduleStatus] = None
    session_type: Optional[SessionType] = None


class ScheduleResponse(BaseModel):
    """Schema for schedule response"""
    schedule_id: int
    patient_id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    notes: Optional[str]
    status: str
    session_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Message Schemas ============

class MessageCreate(BaseModel):
    """Schema for creating a message"""
    receiver_id: UUID
    content: str = Field(..., min_length=1, max_length=5000)


class MessageUpdate(BaseModel):
    """Schema for updating a message (mark as read)"""
    is_read: bool


class MessageResponse(BaseModel):
    """Schema for message response"""
    message_id: int
    sender_id: UUID
    receiver_id: UUID
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Notification Schemas ============

class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    user_id: UUID
    title: Optional[str] = Field(None, max_length=100)
    message: str
    type: str = Field(default="info", max_length=20)


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    is_read: bool


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    notification_id: int
    user_id: UUID
    title: Optional[str]
    message: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
