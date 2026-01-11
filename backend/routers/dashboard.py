from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from uuid import UUID
import uuid
from database import get_db
from models import User, WorkoutSession, SessionDetail, BrainExerciseSession


router = APIRouter(
    prefix="/api",
    tags=["dashboard"]
)

@router.get("/overall-stats")
async def get_overall_stats(user_id: UUID = Query(...), db: Session = Depends(get_db)):
    """Get overall stats for a patient"""
    # Total sessions
    total_sessions = db.query(WorkoutSession).filter(WorkoutSession.user_id == user_id).count()
    
    # Total reps (from SessionDetail)
    total_reps = db.query(func.sum(SessionDetail.reps_completed)).join(WorkoutSession).filter(
        WorkoutSession.user_id == user_id
    ).scalar() or 0
    
    # Total duration
    total_duration = db.query(func.sum(SessionDetail.duration_seconds)).join(WorkoutSession).filter(
        WorkoutSession.user_id == user_id
    ).scalar() or 0
    
    # Total days
    total_days = db.query(func.count(func.distinct(func.date(WorkoutSession.start_time)))).filter(
        WorkoutSession.user_id == user_id
    ).scalar() or 0
    
    return {
        "total_sessions": total_sessions,
        "total_reps": int(total_reps),
        "total_duration": int(total_duration),
        "total_days": total_days
    }

@router.get("/weekly-progress")
async def get_weekly_progress(user_id: UUID = Query(...), db: Session = Depends(get_db)):
    """Get recent exercise history for a patient"""
    # Get last 10 session details
    history = db.query(SessionDetail).join(WorkoutSession).filter(
        WorkoutSession.user_id == user_id
    ).order_by(SessionDetail.completed_at.desc()).limit(10).all()
    
    return [
        {
            "exercise_type": h.exercise_type,
            "max_reps": h.reps_completed,
            "start_time": h.completed_at - timedelta(seconds=h.duration_seconds),
            "end_time": h.completed_at
        }
        for h in history
    ]

@router.get("/patient/charts/{patient_id}")
async def get_patient_charts(patient_id: UUID, db: Session = Depends(get_db)):
    """Get chart data for a patient"""
    # 1. Weekly Activity (Reps per day for last 7 days)
    today = date.today()
    last_week = today - timedelta(days=7)
    
    weekly_data = db.query(
        func.date(SessionDetail.completed_at).label('date'),
        func.sum(SessionDetail.reps_completed).label('reps')
    ).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id,
        func.date(SessionDetail.completed_at) >= last_week
    ).group_by(func.date(SessionDetail.completed_at)).all()
    
    # 2. Accuracy Trend
    accuracy_data = db.query(
        func.date(SessionDetail.completed_at).label('date'),
        func.avg(SessionDetail.accuracy_score).label('score')
    ).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).group_by(func.date(SessionDetail.completed_at)).order_by('date').limit(10).all()
    
    # 3. Muscle Focus (Exercise distribution)
    muscle_data = db.query(
        SessionDetail.exercise_type,
        func.count(SessionDetail.detail_id).label('count')
    ).join(WorkoutSession).filter(
        WorkoutSession.user_id == patient_id
    ).group_by(SessionDetail.exercise_type).all()
    
    return {
        "weekly_activity": [{"date": str(d.date), "reps": int(d.reps)} for d in weekly_data],
        "accuracy_trend": [{"date": str(d.date), "score": float(d.score)} for d in accuracy_data],
        "muscle_focus": [{"exercise_type": d.exercise_type, "count": d.count} for d in muscle_data]
    }

@router.get("/today-progress")
async def get_today_progress_all(db: Session = Depends(get_db)):
    """Get recent activity for all patients (for doctor dashboard)"""
    # Consolidated to use SessionDetail joined with WorkoutSession and User
    logs = db.query(SessionDetail).join(WorkoutSession).join(User, WorkoutSession.user_id == User.user_id).filter(
        func.date(SessionDetail.completed_at) == date.today()
    ).order_by(desc(SessionDetail.completed_at)).limit(10).all()
    
    return [{
        "id": str(uuid.uuid4()),
        "user_id": str(l.session.user_id),
        "full_name": l.session.user.full_name if l.session.user else "Unknown",
        "exercise_type": l.exercise_type,
        "created_at": l.completed_at.isoformat() if l.completed_at else None,
        "rep_count": l.reps_completed
    } for l in logs]

