from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from database import get_db
from models import User, MedicalRecord, PatientNote, WeekPlan, SessionDetail, WorkoutSession
from dependencies import get_current_user, get_current_doctor, get_current_patient, verify_patient_access
from schemas import UserResponse, PatientCreate, MedicalRecordUpdate, PatientNoteCreate
from utils import paginate


router = APIRouter(
    prefix="/api",
    tags=["patients"]
)

from utils import paginate, Page

@router.get("/patients", response_model=Page[UserResponse])
async def get_patients(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_doctor)
):
    """Get all patients with pagination"""
    query = db.query(User).filter(User.role == 'patient').order_by(User.full_name)
    return paginate(query, page, size)


@router.post("/users")
@router.post("/patients")
async def create_user(user: PatientCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):

    """Create new user (Doctor creates Patient)"""
    from auth import get_password_hash
    # Check existence
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")
    
    try:
        new_user = User(
            username=user.username,
            password_hash=get_password_hash(user.password),
            full_name=user.full_name,
            email=user.email,
            role=user.role.value if hasattr(user.role, 'value') else user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"user_id": str(new_user.user_id), "message": "User created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/demo")
async def get_demo_users(db: Session = Depends(get_db)):
    """Get demo users for login screen"""
    doctors = db.query(User).filter(User.role == 'doctor').limit(3).all()
    patients = db.query(User).filter(User.role == 'patient').limit(5).all()
    
    return {
        "doctors": [{"username": u.username, "full_name": u.full_name} for u in doctors],
        "patients": [{"username": u.username, "full_name": u.full_name} for u in patients]
    }

@router.get("/patient-notes/{patient_id}")
async def get_patient_notes(patient_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get notes for a patient"""
    verify_patient_access(patient_id, current_user, db)
    notes = db.query(PatientNote).filter(PatientNote.patient_id == patient_id).order_by(desc(PatientNote.created_at)).all()
    
    return [
        {
            "note_id": note.note_id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at,
            "doctor_name": note.doctor.full_name if note.doctor else "Unknown"
        }
        for note in notes
    ]

@router.post("/patient-notes")
async def add_patient_note(data: PatientNoteCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Add a note for a patient"""
    try:
        note = PatientNote(
            patient_id=data.patient_id,
            doctor_id=current_doctor.user_id,
            title=data.title,
            content=data.content
        )
        db.add(note)
        db.commit()
        return {"message": "Note added"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/patient-logs/{patient_id}")
async def get_patient_logs(patient_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get detailed exercise logs for a patient"""
    verify_patient_access(patient_id, current_user, db)
    
    results = db.query(
        SessionDetail.exercise_type,
        SessionDetail.reps_completed.label("rep_number"),
        SessionDetail.duration_seconds.label("rep_duration_seconds"),
        WorkoutSession.start_time,
        WorkoutSession.end_time,
        SessionDetail.completed_at,
        SessionDetail.accuracy_score
    ).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).order_by(desc(SessionDetail.completed_at)).limit(50).all()
    
    return [
        {
            "exercise_type": r.exercise_type,
            "rep_number": r.rep_number,
            "rep_duration_seconds": r.rep_duration_seconds,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "completed_at": r.completed_at,
            "accuracy_score": float(r.accuracy_score) if r.accuracy_score else 0
        }
        for r in results
    ]

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: UUID, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Delete a patient and all related data"""
    patient = db.query(User).filter(User.user_id == patient_id, User.role == 'patient').first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    try:
        db.delete(patient)
        db.commit()
        return {"message": "Patient deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


from sqlalchemy import func
from models import Assignment

@router.get("/patients/{patient_id}/stats")
async def get_patient_stats(patient_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get comprehensive stats for a patient - replaces mocked patient stats"""
    verify_patient_access(patient_id, current_user, db)
    
    # 1. Total workout sessions
    total_sessions = db.query(WorkoutSession).filter(WorkoutSession.user_id == patient_id).count()
    
    # 2. Total time (in hours)
    total_seconds = db.query(func.sum(SessionDetail.duration_seconds)).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).scalar() or 0
    total_hours = round(total_seconds / 3600, 1)
    
    # 3. Average accuracy score
    avg_score = db.query(func.avg(SessionDetail.accuracy_score)).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).scalar() or 0
    avg_score = round(float(avg_score), 1) if avg_score else 0
    
    # 4. Compliance rate (completed assignments / total assignments)
    total_assignments = db.query(Assignment).filter(Assignment.patient_id == patient_id).count()
    completed_assignments = db.query(Assignment).filter(
        Assignment.patient_id == patient_id,
        Assignment.is_completed == True
    ).count()
    compliance = round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0)
    
    return {
        "compliance": compliance,
        "sessions": total_sessions,
        "totalTime": total_hours,
        "avgScore": avg_score
    }


