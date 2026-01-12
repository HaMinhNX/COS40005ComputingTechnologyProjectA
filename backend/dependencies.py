"""
FastAPI dependencies for authentication and authorization.
This module provides security dependencies to protect endpoints and verify user permissions.
"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import os

from database import get_db
from models import User
from auth import verify_token
from enums import UserRole

# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if credentials is None:
        with open("debug_auth.log", "a") as f:
            f.write("DEBUG: No credentials provided\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    with open("debug_auth.log", "a") as f:
        f.write(f"DEBUG: Token received: {token[:10]}...\n")
    
    # Verify and decode token
    payload = verify_token(token)
    if payload is None:
        with open("debug_auth.log", "a") as f:
            f.write("DEBUG: Token verification failed\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    with open("debug_auth.log", "a") as f:
        f.write(f"DEBUG: Payload: {payload}\n")
    
    # Extract user_id from token
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_doctor(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is a doctor.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User: The doctor user object
        
    Raises:
        HTTPException: If user is not a doctor
    """
    if current_user.role != UserRole.DOCTOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires doctor privileges"
        )
    return current_user


def get_current_patient(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is a patient.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User: The patient user object
        
    Raises:
        HTTPException: If user is not a patient
    """
    if current_user.role != UserRole.PATIENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires patient privileges"
        )
    return current_user


def verify_patient_access(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to verify that the current user has access to a specific patient's data.
    Doctors can access any patient, patients can only access their own data.
    
    Args:
        patient_id: The patient ID to check access for
        current_user: The authenticated user
        db: Database session
        
    Returns:
        User: The patient user object if access is granted
        
    Raises:
        HTTPException: If user doesn't have access to this patient
    """
    # Doctors can access any patient
    if current_user.role == UserRole.DOCTOR.value:
        patient = db.query(User).filter(
            User.user_id == patient_id,
            User.role == UserRole.PATIENT.value
        ).first()
        
        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return patient
    
    # Patients can only access their own data
    if current_user.role == UserRole.PATIENT.value:
        if current_user.user_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this patient's data"
            )
        return current_user
    
    # Unknown role
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid user role"
    )


def verify_doctor_patient_relationship(
    patient_id: UUID,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to verify that a doctor has an existing relationship with a patient.
    This checks if the doctor has created any assignments or schedules for the patient.
    
    Args:
        patient_id: The patient ID to check relationship for
        current_user: The authenticated doctor
        db: Database session
        
    Returns:
        User: The patient user object if relationship exists
        
    Raises:
        HTTPException: If no relationship exists or patient not found
    """
    from models import Assignment, Schedule
    
    # Check if patient exists
    patient = db.query(User).filter(
        User.user_id == patient_id,
        User.role == UserRole.PATIENT.value
    ).first()
    
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if doctor has any assignments or schedules with this patient
    has_assignment = db.query(Assignment).filter(
        Assignment.doctor_id == current_user.user_id,
        Assignment.patient_id == patient_id
    ).first() is not None
    
    has_schedule = db.query(Schedule).filter(
        Schedule.doctor_id == current_user.user_id,
        Schedule.patient_id == patient_id
    ).first() is not None
    
    if not (has_assignment or has_schedule):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have an established relationship with this patient"
        )
    
    return patient


def verify_assignment_access(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dependency to verify that the current user has access to a specific assignment.
    
    Args:
        assignment_id: The assignment ID to check access for
        current_user: The authenticated user
        db: Database session
        
    Returns:
        Assignment: The assignment object if access is granted
        
    Raises:
        HTTPException: If user doesn't have access to this assignment
    """
    from models import Assignment
    
    assignment = db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()
    
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Doctors can access assignments they created
    if current_user.role == UserRole.DOCTOR.value:
        if assignment.doctor_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this assignment"
            )
        return assignment
    
    # Patients can access their own assignments
    if current_user.role == UserRole.PATIENT.value:
        if assignment.patient_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this assignment"
            )
        return assignment
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid user role"
    )


def verify_medical_record_access(
    patient_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dependency to verify access to medical records.
    Only doctors and the patient themselves can access medical records.
    
    Args:
        patient_id: The patient ID whose medical record is being accessed
        current_user: The authenticated user
        db: Database session
        
    Returns:
        User: The patient user object if access is granted
        
    Raises:
        HTTPException: If user doesn't have access to this medical record
    """
    return verify_patient_access(patient_id, current_user, db)


def optional_auth(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns user if valid token is provided, None otherwise.
    Useful for endpoints that work differently for authenticated vs anonymous users.
    
    Args:
        authorization: Optional Authorization header
        db: Database session
        
    Returns:
        Optional[User]: The authenticated user or None
    """
    if authorization is None or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if payload is None:
        return None
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None
    
    try:
        user_id = UUID(user_id_str)
        user = db.query(User).filter(User.user_id == user_id).first()
        return user
    except (ValueError, Exception):
        return None


# Environment variable validation
def validate_environment():
    """
    Validates that all required environment variables are set.
    Should be called at application startup.
    
    Raises:
        RuntimeError: If required environment variables are missing
    """
    required_vars = ["SECRET_KEY", "DATABASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or (var == "SECRET_KEY" and value == "your_super_secret_key_change_this_in_production"):
            missing_vars.append(var)
    
    if missing_vars:
        raise RuntimeError(
            f"Missing or invalid required environment variables: {', '.join(missing_vars)}. "
            f"Please set them in your .env file."
        )
