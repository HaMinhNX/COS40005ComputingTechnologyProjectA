from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from database import get_db
from models import User, Schedule, Notification
from dependencies import get_current_user, get_current_doctor, verify_patient_access
from schemas import ScheduleCreate

router = APIRouter(
    prefix="/api",
    tags=["schedules"]
)

@router.get("/schedules/{doctor_id}")
async def get_doctor_schedules(doctor_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get schedules for a doctor"""
    return db.query(Schedule).filter(Schedule.doctor_id == doctor_id).all()

@router.get("/patient-schedules/{patient_id}")
async def get_patient_schedules(patient_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get schedules for a patient"""
    verify_patient_access(patient_id, current_user, db)
    return db.query(Schedule).filter(Schedule.patient_id == patient_id).all()

@router.post("/schedules")
async def create_schedule(data: ScheduleCreate, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Create a new schedule/appointment"""
    try:
        new_schedule = Schedule(
            patient_id=data.patient_id,
            doctor_id=current_doctor.user_id,
            start_time=data.start_time,
            end_time=data.end_time,
            notes=data.notes,
            session_type=data.session_type.value if hasattr(data.session_type, 'value') else data.session_type
        )
        db.add(new_schedule)
        
        # Create notification for patient
        notif = Notification(
            user_id=data.patient_id,
            title='Lịch hẹn mới',
            message=f"Bác sĩ đã đặt lịch hẹn mới vào lúc {data.start_time.strftime('%H:%M %d/%m/%Y')}",
            type='info'
        )
        db.add(notif)
        
        db.commit()
        db.refresh(new_schedule)
        return new_schedule
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int, db: Session = Depends(get_db), current_doctor: User = Depends(get_current_doctor)):
    """Delete a schedule"""
    schedule = db.query(Schedule).filter(
        Schedule.schedule_id == schedule_id,
        Schedule.doctor_id == current_doctor.user_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found or unauthorized")
        
    try:
        db.delete(schedule)
        db.commit()
        return {"message": "Schedule deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
