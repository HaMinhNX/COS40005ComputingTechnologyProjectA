from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
import time
from database import get_db
from models import User, WorkoutSession, SessionDetail, BrainExerciseLog, BrainExerciseSession

from dependencies import get_current_user, get_current_patient
from schemas.exercise import (
    WorkoutSessionCreate, WorkoutSessionEnd, SessionDetailCreate,
    ProcessRequest, ProcessResponse, LandmarkData
)
from exercise_logic import (
    AngleCalculator, Landmark, EXERCISE_COUNTER, SquatState, 
    BicepCurlState, ShoulderFlexionState, KneeRaiseState,
    calculate_all_angles, get_state_name, prev_reps
)

router = APIRouter(
    prefix="/api",
    tags=["exercises"]
)

@router.post("/select_exercise")
async def select_exercise(exercise_name: str):
    """Reset state for a specific exercise"""
    EXERCISE_COUNTER.reset_state(exercise_name)
    prev_reps[exercise_name] = 0
    return {"message": f"State reset for {exercise_name}"}

@router.post("/process_landmarks", response_model=ProcessResponse)

async def process_landmarks_api(request: ProcessRequest):
    try:
        if not request.landmarks:
            raise HTTPException(status_code=400, detail="No landmarks provided")

        # Convert schemas.LandmarkData to exercise_logic.Landmark
        lm_objects = [Landmark(lm.x, lm.y, lm.z, lm.visibility) for lm in request.landmarks]
        
        angles = calculate_all_angles(lm_objects)
        if 'error' in angles:
            raise HTTPException(status_code=400, detail=angles['error'])

        left_shoulder = lm_objects[11]; right_shoulder = lm_objects[12]
        left_elbow = lm_objects[13]; right_elbow = lm_objects[14]
        left_wrist = lm_objects[15]; right_wrist = lm_objects[16]
        left_hip = lm_objects[23]; right_hip = lm_objects[24]
        left_knee = lm_objects[25]; right_knee = lm_objects[26]
        left_ankle = lm_objects[27]; right_ankle = lm_objects[28]

        if request.current_exercise not in prev_reps:
            prev_reps[request.current_exercise] = 0

        # Process
        feedback = []
        if request.current_exercise == 'bicep-curl':
            state, feedback = EXERCISE_COUNTER.process_bicep_curl(
                left_shoulder=left_shoulder, left_elbow=left_elbow, left_wrist=left_wrist, left_hip=left_hip,
                right_shoulder=right_shoulder, right_elbow=right_elbow, right_wrist=right_wrist, right_hip=right_hip,
                left_bicep_angle=angles['left_bicep_angle'], right_bicep_angle=angles['right_bicep_angle'],
                elbow_torso_result=angles['elbow_torso_result'], hip_shoulder_angle=angles['hip_shoulder_angle']
            )
        elif request.current_exercise == 'squat':
            state, feedback = EXERCISE_COUNTER.process_squat(
                knee_angle=angles['knee_angle_avg'], back_angle=angles['back_angle'],
                left_hip=left_hip, right_hip=right_hip, left_knee=left_knee, right_knee=right_knee,
                left_ankle=left_ankle, right_ankle=right_ankle,
                left_shoulder=left_shoulder, right_shoulder=right_shoulder
            )
        elif request.current_exercise == 'shoulder-flexion':
            state, feedback = EXERCISE_COUNTER.process_shoulder_flexion(
                left_hip=left_hip, left_shoulder=left_shoulder, left_elbow=left_elbow, left_wrist=left_wrist,
                right_hip=right_hip, right_shoulder=right_shoulder, right_elbow=right_elbow, right_wrist=right_wrist,
                left_flexion_angle=angles['left_flexion_angle'], right_flexion_angle=angles['right_flexion_angle'],
                left_elbow_angle=angles['left_elbow_angle'], right_elbow_angle=angles['right_elbow_angle'],
                hip_shoulder_angle=angles['hip_shoulder_angle']
            )
        elif request.current_exercise == 'knee-raise':
            state, feedback = EXERCISE_COUNTER.process_knee_raise(
                left_hip=left_hip, left_knee=left_knee, left_ankle=left_ankle,
                right_hip=right_hip, right_knee=right_knee, right_ankle=right_ankle,
                left_shoulder=left_shoulder, left_wrist=left_wrist,
                right_shoulder=right_shoulder, right_wrist=right_wrist,
                left_knee_angle=angles['left_knee_angle'], right_knee_angle=angles['right_knee_angle'],
                left_flexion_angle=angles['left_flexion_angle'], right_flexion_angle=angles['right_flexion_angle'],
                hip_shoulder_angle=angles['hip_shoulder_angle']
            )

        # State names
        squat_state_name = get_state_name(SquatState, EXERCISE_COUNTER.squat_state)
        curl_state_name = get_state_name(BicepCurlState, EXERCISE_COUNTER.bicep_curl_state)
        shoulder_flexion_state_name = get_state_name(ShoulderFlexionState, EXERCISE_COUNTER.shoulder_flexion_state)
        knee_raise_state_name = get_state_name(KneeRaiseState, EXERCISE_COUNTER.knee_raise_state)

        # Rep count
        new_rep = {
            'squat': EXERCISE_COUNTER.squat_counter,
            'bicep-curl': EXERCISE_COUNTER.curl_counter,
            'shoulder-flexion': EXERCISE_COUNTER.shoulder_flexion_counter,
            'knee-raise': EXERCISE_COUNTER.knee_raise_counter
        }.get(request.current_exercise, 0)

        # Log to DB if rep increased
        if new_rep > prev_reps[request.current_exercise]:
            prev_reps[request.current_exercise] = new_rep
            # We can log here if needed, but usually it's better to log at the end of session
            # or via a separate /session/log endpoint called by the frontend.
            # For backward compatibility with main.py, we could log to ExerciseLogSimple.

        return ProcessResponse(
            squat_count=EXERCISE_COUNTER.squat_counter,
            curl_count=EXERCISE_COUNTER.curl_counter,
            shoulder_flexion_count=EXERCISE_COUNTER.shoulder_flexion_counter,
            knee_raise_count=EXERCISE_COUNTER.knee_raise_counter,
            total_reps=EXERCISE_COUNTER.total_reps,
            squat_state_name=squat_state_name,
            curl_state_name=curl_state_name,
            shoulder_flexion_state_name=shoulder_flexion_state_name,
            knee_raise_state_name=knee_raise_state_name,
            feedback=", ".join(feedback) if feedback else ""
        )
    except Exception as e:
        print(f"[ERROR] process_landmarks failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/start")
async def start_session(data: WorkoutSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Start a new workout session"""
    try:
        new_session = WorkoutSession(
            user_id=current_user.user_id,
            plan_id=data.plan_id
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/log")
async def log_session_detail(data: SessionDetailCreate, db: Session = Depends(get_db)):
    """Log detail for an exercise in a session"""
    try:
        new_detail = SessionDetail(
            session_id=data.session_id,
            exercise_type=data.exercise_type,
            reps_completed=data.reps_completed,
            duration_seconds=data.duration_seconds,
            mistakes_count=data.mistakes_count,
            accuracy_score=data.accuracy_score,
            feedback=data.feedback
        )

        db.add(new_detail)
        db.commit()
        db.refresh(new_detail)
        return new_detail
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/end/{session_id}")
async def end_session(session_id: UUID, db: Session = Depends(get_db)):
    """End a workout session"""
    session = db.query(WorkoutSession).filter(WorkoutSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from datetime import datetime
    session.end_time = datetime.now()
    session.status = 'completed'
    
    try:
        db.commit()
        return {"message": "Session ended"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Brain Exercises
@router.post("/brain-exercise/submit")
async def submit_brain_exercise(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Submit a single brain exercise attempt"""
    try:
        new_log = BrainExerciseLog(
            user_id=UUID(data['user_id']),
            exercise_type=data['exercise_type'],
            is_correct=data['is_correct'],
            question_number=data.get('question_number')
        )
        db.add(new_log)
        db.commit()
        return {"message": "Attempt logged"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/brain-exercise/complete")
async def complete_brain_exercise(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Complete a brain exercise session"""
    try:
        percentage = (data['score'] / data['total_questions']) * 100
        new_session = BrainExerciseSession(
            user_id=UUID(data['user_id']),
            exercise_type=data['exercise_type'],
            score=data['score'],
            total_questions=data['total_questions'],
            percentage=percentage
        )
        db.add(new_session)
        db.commit()
        return {"message": "Session completed"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/brain-exercise/stats/{user_id}")
async def get_brain_stats(user_id: UUID, db: Session = Depends(get_db)):
    """Get brain exercise stats for a user"""
    from sqlalchemy import func
    from datetime import date
    
    today_score = db.query(func.sum(BrainExerciseSession.score)).filter(
        BrainExerciseSession.user_id == user_id,
        func.date(BrainExerciseSession.created_at) == date.today()
    ).scalar() or 0
    
    # Simple streak calculation (placeholder)
    streak = 1 
    
    return {
        "today_score": int(today_score),
        "streak": streak
    }
