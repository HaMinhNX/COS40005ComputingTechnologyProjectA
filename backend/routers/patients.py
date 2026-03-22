from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from database import get_db
from models import User, MedicalRecord, PatientNote, SessionDetail, WorkoutSession, BrainExerciseSession
from dependencies import get_current_user, get_current_doctor
from middleware.ownership import ResourceAccess
from schemas import UserResponse, PatientCreate, PatientNoteCreate
from utils import paginate
from datetime import datetime



router = APIRouter(
    prefix="/api",
    tags=["patients"]
)

from utils import Page

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
async def get_patient_notes(
    patient_id: UUID, 
    db: Session = Depends(get_db), 
    patient: User = Depends(ResourceAccess.patient)
):
    """Get notes for a patient"""
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
async def add_patient_note(
    data: PatientNoteCreate, 
    db: Session = Depends(get_db), 
    current_doctor: User = Depends(get_current_doctor)
):
    """Add a note for a patient"""
    # Verify relationship
    await ResourceAccess.patient(data.patient_id, current_doctor, db)
    
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
async def get_patient_logs(
    patient_id: UUID, 
    db: Session = Depends(get_db), 
    patient: User = Depends(ResourceAccess.patient)
):
    """Get detailed exercise logs for a patient"""
    
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
async def get_patient_stats(
    patient_id: UUID, 
    db: Session = Depends(get_db), 
    patient: User = Depends(ResourceAccess.patient)
):
    """Get comprehensive stats for a patient"""
    
    # 1. Total workout sessions
    total_sessions = db.query(WorkoutSession).filter(WorkoutSession.user_id == patient_id).count()
    
    # 2. Total time (in hours)
    total_seconds = db.query(func.sum(SessionDetail.duration_seconds)).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).scalar() or 0
    total_hours = round(float(total_seconds / 3600), 1)
    
    # 3. Average accuracy score
    avg_score = db.query(func.avg(SessionDetail.accuracy_score)).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).scalar() or 0
    avg_score = round(float(avg_score), 1) if avg_score else 0.0
    
    # 4. Compliance rate (completed assignments / total assignments)
    total_assignments = db.query(Assignment).filter(Assignment.patient_id == patient_id).count()
    completed_assignments = db.query(Assignment).filter(
        Assignment.patient_id == patient_id,
        Assignment.is_completed == True
    ).count()
    compliance = round(float((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0))
    
    return {
        "compliance": compliance,
        "sessions": total_sessions,
        "totalTime": float(total_hours),
        "avgScore": float(avg_score)
    }


@router.get("/patients/{patient_id}/report")
async def get_patient_report(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a comprehensive clinical report for a patient."""
    # Verify access
    patient = await ResourceAccess.patient(patient_id, current_user, db)
    
    # 1. Medical context
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    
    # 2. Physical Workout Summary
    total_physical_reps = db.query(func.sum(SessionDetail.reps_completed)).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).scalar() or 0
    physical_sessions_count = db.query(WorkoutSession).filter(WorkoutSession.user_id == patient_id).count()
    
    # 3. Brain Exercise Summary
    brain_sessions_count = db.query(BrainExerciseSession).filter(BrainExerciseSession.user_id == patient_id).count()
    avg_brain_score = db.query(func.avg(BrainExerciseSession.percentage)).filter(
        BrainExerciseSession.user_id == patient_id
    ).scalar() or 0
    
    # 4. Recent Notes
    notes = db.query(PatientNote).filter(PatientNote.patient_id == patient_id).order_by(desc(PatientNote.created_at)).limit(5).all()
    
    return {
        "patient_info": {
            "name": patient.full_name,
            "diagnosis": record.diagnosis if record else "N/A",
            "treatment_plan": record.treatment_plan if record else "N/A"
        },
        "metrics": {
            "total_physical_reps": int(total_physical_reps),
            "physical_sessions_count": physical_sessions_count,
            "avg_brain_score": round(float(avg_brain_score), 1),
            "brain_sessions_count": brain_sessions_count
        },
        "recent_notes": [
            {"title": n.title, "content": n.content, "date": n.created_at.strftime("%Y-%m-%d")}
            for n in notes
        ],
        "report_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
