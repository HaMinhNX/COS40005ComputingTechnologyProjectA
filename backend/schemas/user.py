"""
Pydantic schemas for User-related operations.
Provides request/response validation and API documentation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enums import UserRole


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
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    role: UserRole

    @validator('password')
    def validate_password(cls, v):
        """Ensure password meets security requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        """Ensure password meets security requirements if provided"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# ============ Response Schemas ============

class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    user_id: UUID
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True  # Allows creation from ORM models


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

    class Config:
        from_attributes = True


# ============ Patient-Specific Schemas ============

class PatientCreate(BaseModel):
    """Schema for creating a new patient (by doctor)"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., max_length=100)

    @validator('password')
    def validate_password(cls, v):
        """Ensure password meets security requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PatientResponse(UserResponse):
    """Extended patient response with medical info"""
    pass  # Can add patient-specific fields here


class DoctorResponse(UserResponse):
    """Extended doctor response"""
    pass  # Can add doctor-specific fields here
