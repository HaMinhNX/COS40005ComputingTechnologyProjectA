from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from uuid import UUID
from database import get_db
from models import User, WorkoutSession, SessionDetail, Assignment

router = APIRouter(
    prefix="/api/doctor",
    tags=["doctor"]
)

@router.get("/overview")
async def get_doctor_overview(db: Session = Depends(get_db)):
    """Get overview stats for doctor dashboard"""
    total_patients = db.query(User).filter(User.role == 'patient').count()
    active_patients = db.query(func.count(func.distinct(WorkoutSession.user_id))).filter(
        WorkoutSession.start_time >= datetime.now() - timedelta(days=7)
    ).scalar() or 0
    
    # Critical patients (placeholder logic: those with low accuracy in last session)
    critical_patients = db.query(func.count(func.distinct(WorkoutSession.user_id))).join(SessionDetail).filter(
        SessionDetail.accuracy_score < 60,
        WorkoutSession.start_time >= datetime.now() - timedelta(days=3)
    ).scalar() or 0
    
    return {
        "total_patients": total_patients,
        "active_patients": active_patients,
        "critical_patients": critical_patients,
        "avg_form_score": 85 # Placeholder
    }

@router.get("/adherence")
async def get_patient_adherence(db: Session = Depends(get_db)):
    """Get patient adherence data"""
    # Placeholder logic
    return [
        {"name": "Nguyễn Văn A", "score": 95},
        {"name": "Trần Thị B", "score": 82},
        {"name": "Lê Văn C", "score": 45}
    ]

@router.get("/common-issues")
async def get_common_issues(db: Session = Depends(get_db)):
    """Get common issues across patients"""
    # Placeholder logic
    return [
        {"issue": "Sai tư thế Squat", "count": 12},
        {"issue": "Tốc độ quá nhanh", "count": 8},
        {"issue": "Thiếu biên độ", "count": 5}
    ]

@router.get("/doctor-id")
async def get_doctor_id(db: Session = Depends(get_db)):
    """Get the first doctor ID for demo purposes"""
    doctor = db.query(User).filter(User.role == 'doctor').first()
    if doctor:
        return {"doctor_id": str(doctor.user_id)}
    return {"doctor_id": None}

