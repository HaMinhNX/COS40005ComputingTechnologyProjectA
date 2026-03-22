from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID
from database import get_db
from models import User, WorkoutSession, SessionDetail, BrainExerciseLog, BrainExerciseSession

from dependencies import get_current_user
from middleware.ownership import ResourceAccess
from enums import ExerciseType, DAILY_TARGETS
from schemas.exercise import (
    WorkoutSessionCreate, SessionDetailCreate,
    ProcessRequest, ProcessResponse, WorkoutSessionResponse, SessionDetailResponse
)
from exercise_logic import (
    Landmark, EXERCISE_COUNTER, SquatState, 
    BicepCurlState, ShoulderFlexionState, KneeRaiseState,
    calculate_all_angles, get_state_name, prev_reps
)

router = APIRouter(
    prefix="/api",
    tags=["exercises"]
)

@router.get("/exercises/config")
async def get_exercises_config(current_user: User = Depends(get_current_user)):
    """Get synchronized exercise configuration and mapping"""
    return {
        "exercises": [
            {"id": e.value, "name": e.value.replace("-", " ").title(), "icon": "Dumbbell"} 
            for e in ExerciseType
        ],
        "daily_targets": {k.value: v for k, v in DAILY_TARGETS.items()}
    }

@router.post("/select_exercise")
async def select_exercise(exercise_name: str):
    """Reset state for a specific exercise"""
    EXERCISE_COUNTER.reset_state(exercise_name)
    prev_reps[exercise_name] = 0
    return {"message": f"State reset for {exercise_name}"}

# Mapping display names/Vietnamese names to strict API keys
EXERCISE_NAME_MAPPING = {
    "Gập bắp tay": "bicep-curl",
    "Bicep Curl": "bicep-curl",
    "Đứng lên ngồi xuống": "squat",
    "Squat": "squat",
    "Nâng vai": "shoulder-flexion",
    "Shoulder Flexion": "shoulder-flexion",
    "Shoulder Press": "shoulder-flexion",
    "Nâng đầu gối": "knee-raise",
    "Knee Raise": "knee-raise"
}

@router.post("/process_landmarks", response_model=ProcessResponse)
async def process_landmarks_api(request: ProcessRequest):
    try:
        if not request.landmarks:
            raise HTTPException(status_code=400, detail="No landmarks provided")

        # Robust Name Mapping: Convert display names into strict API keys
        current_ex = request.current_exercise
        if current_ex in EXERCISE_NAME_MAPPING:
            current_ex = EXERCISE_NAME_MAPPING[current_ex]
        
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

        if current_ex not in prev_reps:
            prev_reps[current_ex] = 0

        # Process
        feedback = []
        if current_ex == 'bicep-curl':
            state, feedback = EXERCISE_COUNTER.process_bicep_curl(
                landmarks=lm_objects,
                left_shoulder=left_shoulder, left_elbow=left_elbow, left_wrist=left_wrist, left_hip=left_hip,
                right_shoulder=right_shoulder, right_elbow=right_elbow, right_wrist=right_wrist, right_hip=right_hip,
                left_bicep_angle=angles['left_bicep_angle'], right_bicep_angle=angles['right_bicep_angle'],
                elbow_torso_result=angles['elbow_torso_result'], hip_shoulder_angle=angles['hip_shoulder_angle']
            )
        elif current_ex == 'squat':
            state, feedback = EXERCISE_COUNTER.process_squat(
                landmarks=lm_objects,
                knee_angle=angles['knee_angle_avg'], back_angle=angles['back_angle'],
                left_hip=left_hip, right_hip=right_hip, left_knee=left_knee, right_knee=right_knee,
                left_ankle=left_ankle, right_ankle=right_ankle,
                left_shoulder=left_shoulder, right_shoulder=right_shoulder
            )
        elif current_ex == 'shoulder-flexion':
            state, feedback = EXERCISE_COUNTER.process_shoulder_flexion(
                landmarks=lm_objects,
                left_hip=left_hip, left_shoulder=left_shoulder, left_elbow=left_elbow, left_wrist=left_wrist,
                right_hip=right_hip, right_shoulder=right_shoulder, right_elbow=right_elbow, right_wrist=right_wrist,
                left_flexion_angle=angles['left_flexion_angle'], right_flexion_angle=angles['right_flexion_angle'],
                left_elbow_angle=angles['left_elbow_angle'], right_elbow_angle=angles['right_elbow_angle'],
                hip_shoulder_angle=angles['hip_shoulder_angle']
            )
        elif current_ex == 'knee-raise':
            state, feedback = EXERCISE_COUNTER.process_knee_raise(
                landmarks=lm_objects,
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
        }.get(current_ex, 0)

        # Log to DB if rep increased
        if new_rep > prev_reps[current_ex]:
            prev_reps[current_ex] = new_rep
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] process_landmarks failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/start", response_model=WorkoutSessionResponse)
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

@router.post("/session/log", response_model=SessionDetailResponse)
async def log_session_detail(
    data: SessionDetailCreate, 
    db: Session = Depends(get_db),
    current_session: WorkoutSession = Depends(ResourceAccess.session)
):
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
async def end_session(
    session_id: UUID, 
    db: Session = Depends(get_db),
    current_session: WorkoutSession = Depends(ResourceAccess.session)
):
    """End a workout session"""
    # Ownership verified via ResourceAccess.session dependency
    from datetime import datetime
    current_session.end_time = datetime.now()
    current_session.status = 'completed'
    
    try:
        db.commit()
        return {"message": "Session ended"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Brain Exercises
@router.post("/brain-exercise/submit")
async def submit_brain_exercise(
    data: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a single brain exercise attempt"""
    # Verify the user is submitting for themselves (or a doctor for their patient)
    await ResourceAccess.patient(UUID(data['user_id']), current_user, db)
    
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
async def complete_brain_exercise(
    data: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a brain exercise session"""
    # Verify ownership
    await ResourceAccess.patient(UUID(data['user_id']), current_user, db)
    
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
async def get_brain_stats(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get brain exercise stats for a user"""
    # Verify access to this user's stats
    await ResourceAccess.patient(user_id, current_user, db)
    
    from sqlalchemy import func
    from datetime import date
    
    today_score = db.query(func.sum(BrainExerciseSession.score)).filter(
        BrainExerciseSession.user_id == user_id,
        func.date(BrainExerciseSession.created_at) == date.today()
    ).scalar() or 0
    
    # Real streak calculation
    from datetime import timedelta
    
    # Get all unique dates where the user had a session, ordered by date desc
    sessions = db.query(func.date(BrainExerciseSession.created_at)).filter(
        BrainExerciseSession.user_id == user_id
    ).distinct().order_by(func.date(BrainExerciseSession.created_at).desc()).all()
    
    dates = [s[0] for s in sessions]
    streak = 0
    if dates:
        curr_date = date.today()
        # If no activity today, check if they had activity yesterday to continue streak
        if dates[0] != curr_date:
            if dates[0] == curr_date - timedelta(days=1):
                curr_date = dates[0]
            else:
                # Streak broken
                streak = 0
        
        if streak == 0 and dates[0] in [curr_date, curr_date - timedelta(days=1)]:
            streak = 1
            for i in range(len(dates) - 1):
                if dates[i] - timedelta(days=1) == dates[i+1]:
                    streak += 1
                else:
                    break
    
    return {
        "today_score": int(today_score),
        "streak": streak
    }
