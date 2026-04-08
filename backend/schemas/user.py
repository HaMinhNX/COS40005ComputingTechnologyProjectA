"""
Pydantic schemas for User-related operations.
Provides request/response validation and API documentation.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enums import UserRole, DoctorApprovalStatus
import re

SPECIAL_CHAR_REGEX = re.compile(r'[!@#$%^&*()\-_=+\[\]{};\':"\\|,.<>/?`~]')


def validate_password_strength(v: str) -> str:
    """Shared password validation – production-grade rules."""
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if len(v) > 40:
        raise ValueError('Password must not exceed 40 characters')
    if not any(c.isupper() for c in v):
        raise ValueError('Password must contain at least one uppercase letter')
    if not any(c.islower() for c in v):
        raise ValueError('Password must contain at least one lowercase letter')
    if not any(c.isdigit() for c in v):
        raise ValueError('Password must contain at least one digit')
    if not SPECIAL_CHAR_REGEX.search(v):
        raise ValueError('Password must contain at least one special character (!@#$%^&* etc.)')
    return v


# ============ Base Schemas ============

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole


# ============ Request Schemas ============

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=40)
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Ensure password meets production security requirements"""
        return validate_password_strength(v)


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class GoogleLogin(BaseModel):
    """Schema for Google OAuth token login"""
    credential: str


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=40)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Ensure password meets security requirements if provided"""
        if v is None:
            return v
        return validate_password_strength(v)

class ForgotPasswordRequest(BaseModel):
    """Schema for requesting a forgot password OTP"""
    email: EmailStr

class VerifyForgotPasswordOTP(BaseModel):
    """Schema for verifying a forgot password OTP"""
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)

class ResetPassword(BaseModel):
    """Schema for resetting password after OTP verification"""
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=40)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Ensure new password meets production security requirements"""
        return validate_password_strength(v)


# ============ Response Schemas ============

class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    user_id: UUID
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    approval_status: Optional[DoctorApprovalStatus] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserWithToken(UserResponse):
    """Schema for login response with JWT token"""
    access_token: str
    token_type: str = "bearer"


class UserListItem(BaseModel):
    """Simplified user schema for list views"""
    user_id: UUID
    username: str
    full_name: Optional[str]
    role: UserRole

    model_config = {"from_attributes": True}


# ============ Patient-Specific Schemas ============

class PatientCreate(BaseModel):
    """Schema for creating a new patient (by doctor)"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=40)
    full_name: str = Field(..., max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Ensure password meets production security requirements"""
        return validate_password_strength(v)


class PatientResponse(UserResponse):
    """Extended patient response with medical info"""
    pass  # Can add patient-specific fields here


class DoctorResponse(UserResponse):
    """Extended doctor response"""
    pass  # Can add doctor-specific fields here
