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


@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary stats with trend calculations"""
    from enums import PatientStatus
    
    # Total patients
    total_patients = db.query(User).filter(User.role == 'patient').count()
    
    # Calculate activity-based status
    seven_days_ago = date.today() - timedelta(days=7)
    three_days_ago = date.today() - timedelta(days=3)
    thirty_days_ago = date.today() - timedelta(days=30)
    sixty_days_ago = date.today() - timedelta(days=60)
    
    # Get patients with recent activity
    active_patient_ids = db.query(WorkoutSession.user_id).filter(
        func.date(WorkoutSession.start_time) >= seven_days_ago
    ).distinct().subquery()
    
    # Count active patients (activity in last 7 days)
    active_count = db.query(User).filter(
        User.role == 'patient',
        User.user_id.in_(db.query(active_patient_ids))
    ).count()
    
    # Needs attention: activity 3-7 days ago but not recently
    needs_attention_ids = db.query(WorkoutSession.user_id).filter(
        func.date(WorkoutSession.start_time) >= seven_days_ago,
        func.date(WorkoutSession.start_time) < three_days_ago
    ).distinct().subquery()
    
    needs_attention_count = db.query(User).filter(
        User.role == 'patient',
        User.user_id.in_(db.query(needs_attention_ids)),
        ~User.user_id.in_(db.query(WorkoutSession.user_id).filter(
            func.date(WorkoutSession.start_time) >= three_days_ago
        ).distinct())
    ).count()
    
    # Avg form score across all patients
    avg_form = db.query(func.avg(SessionDetail.accuracy_score)).scalar() or 0
    
    # --- TREND CALCULATIONS ---
    # Patient growth: compare this month vs last month
    patients_this_month = db.query(User).filter(
        User.role == 'patient',
        func.date(User.created_at) >= thirty_days_ago
    ).count()
    patients_last_month = db.query(User).filter(
        User.role == 'patient',
        func.date(User.created_at) >= sixty_days_ago,
        func.date(User.created_at) < thirty_days_ago
    ).count()
    patient_trend = round(((patients_this_month - patients_last_month) / max(patients_last_month, 1)) * 100) if patients_last_month > 0 else (patients_this_month * 10)
    
    # Activity trend: sessions today vs yesterday
    today_sessions = db.query(WorkoutSession).filter(
        func.date(WorkoutSession.start_time) == date.today()
    ).count()
    yesterday_sessions = db.query(WorkoutSession).filter(
        func.date(WorkoutSession.start_time) == date.today() - timedelta(days=1)
    ).count()
    activity_trend = round(((today_sessions - yesterday_sessions) / max(yesterday_sessions, 1)) * 100) if yesterday_sessions > 0 else (today_sessions * 5)
    
    # New alerts (needs_attention count is the alert count)
    new_alerts = needs_attention_count
    
    return {
        "total_patients": total_patients,
        "active_count": active_count,
        "needs_attention_count": needs_attention_count,
        "inactive_count": total_patients - active_count,
        "avg_form_score": round(float(avg_form), 1) if avg_form else 0,
        "patient_trend": patient_trend,
        "activity_trend": activity_trend,
        "new_alerts": new_alerts
    }


@router.get("/patients-with-status")
async def get_patients_with_status(db: Session = Depends(get_db)):
    """Get all patients with their activity status and last active time - OPTIMIZED"""
    from enums import PatientStatus
    
    # Get all patients
    patients = db.query(User).filter(User.role == 'patient').all()
    patient_ids = [p.user_id for p in patients]
    
    if not patient_ids:
        return []
    
    # Batch query 1: Get last session for all patients in one query
    last_sessions_subq = db.query(
        WorkoutSession.user_id,
        func.max(WorkoutSession.start_time).label('last_time')
    ).filter(
        WorkoutSession.user_id.in_(patient_ids)
    ).group_by(WorkoutSession.user_id).all()
    
    last_session_map = {str(row.user_id): row.last_time for row in last_sessions_subq}
    
    # Batch query 2: Get avg accuracy for all patients in one query
    accuracy_subq = db.query(
        WorkoutSession.user_id,
        func.avg(SessionDetail.accuracy_score).label('avg_score')
    ).join(SessionDetail).filter(
        WorkoutSession.user_id.in_(patient_ids)
    ).group_by(WorkoutSession.user_id).all()
    
    accuracy_map = {str(row.user_id): float(row.avg_score) if row.avg_score else 0 for row in accuracy_subq}
    
    # Batch query 3: Get session counts for all patients in one query
    session_counts_subq = db.query(
        WorkoutSession.user_id,
        func.count(WorkoutSession.session_id).label('count')
    ).filter(
        WorkoutSession.user_id.in_(patient_ids)
    ).group_by(WorkoutSession.user_id).all()
    
    session_count_map = {str(row.user_id): row.count for row in session_counts_subq}
    
    # Build result using pre-fetched data (no more DB calls in loop!)
    result = []
    now = datetime.now()
    
    for patient in patients:
        pid = str(patient.user_id)
        
        # Get last active from map
        last_active = last_session_map.get(pid) or patient.created_at
        
        # Calculate status based on activity
        if last_active:
            if last_active.tzinfo:
                days_since = (now.replace(tzinfo=last_active.tzinfo) - last_active).days
            else:
                days_since = (now - last_active).days
            
            if days_since <= 3:
                status = PatientStatus.ACTIVE.value
            elif days_since <= 7:
                status = PatientStatus.NEEDS_ATTENTION.value
            else:
                status = PatientStatus.INACTIVE.value
        else:
            status = PatientStatus.INACTIVE.value
        
        # Get progress from maps
        avg_accuracy = accuracy_map.get(pid, 0)
        session_count = session_count_map.get(pid, 0)
        
        if avg_accuracy > 0:
            progress = round(avg_accuracy)
        elif session_count > 0:
            progress = min(session_count * 15, 100)
        else:
            progress = 0
        
        result.append({
            "patient_id": pid,
            "full_name": patient.full_name,
            "email": patient.email,
            "status": status,
            "last_active_at": last_active.isoformat() if last_active else None,
            "progress": progress
        })
    
    return result


