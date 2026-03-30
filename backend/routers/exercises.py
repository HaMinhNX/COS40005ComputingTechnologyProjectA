from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID
from database import get_db
from models import User, WorkoutSession, SessionDetail, BrainExerciseLog, BrainExerciseSession, HealthMetrics

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


# ─── SESSION IMPORT ────────────────────────────────────────────────────────────

from fastapi import UploadFile, File
import csv
import io
import json as _json
from datetime import datetime as _dt
import xml.etree.ElementTree as ET

VALID_EXERCISE_TYPES = {"squat", "bicep-curl", "shoulder-flexion", "knee-raise"}

@router.post("/session/import")
async def import_session_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import session data from a CSV, JSON, or XML file.

    CSV format (header row required):
        date, exercise_type, reps_completed, duration_seconds, accuracy_score, feedback

    JSON format (array of objects with the same fields).

    XML format (for smartwatch health data):
        <health-data>
            <metrics date="2024-01-01">
                <heart-rate>75</heart-rate>
                <calories>1400</calories>
                <resting-hr>65</resting-hr>
                <spo2>98</spo2>
                <sleep-quality>85</sleep-quality>
            </metrics>
        </health-data>
    """
    content = await file.read()
    filename = file.filename or ""

    rows = []
    is_health_data = False

    try:
        if filename.endswith(".json"):
            rows = _json.loads(content.decode("utf-8"))
            if not isinstance(rows, list):
                raise ValueError("JSON file must be an array of objects")
        elif filename.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            rows = list(reader)
        elif filename.endswith(".xml"):
            # Parse XML health data
            root = ET.fromstring(content.decode("utf-8"))
            if root.tag == "health-data":
                is_health_data = True
                # For health data, we'll store it differently
                # This will be handled separately below
            else:
                raise ValueError("XML file must have root element 'health-data'")
        else:
            raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file .csv, .json hoặc .xml")
    except (UnicodeDecodeError, ValueError, ET.ParseError) as e:
        raise HTTPException(status_code=400, detail=f"Không thể đọc file: {e}")

    if not rows and not is_health_data:
        raise HTTPException(status_code=400, detail="File không có dữ liệu")

    imported = 0
    errors = []

    if is_health_data:
        # Handle health data import
        try:
            for metrics in root.findall("metrics"):
                date_str = metrics.get("date")
                if not date_str:
                    errors.append("Metrics element missing date attribute")
                    continue

                try:
                    record_date = _dt.fromisoformat(date_str).date()
                except ValueError:
                    errors.append(f"Invalid date format: {date_str}")
                    continue

                # Extract health metrics
                heart_rate = int(metrics.findtext("heart-rate", "0") or "0")
                calories = int(metrics.findtext("calories", "0") or "0")
                resting_hr = int(metrics.findtext("resting-hr", "0") or "0")
                spo2 = int(metrics.findtext("spo2", "0") or "0")
                sleep_quality = int(metrics.findtext("sleep-quality", "0") or "0")
                
                # Optional metrics
                steps = metrics.findtext("steps")
                distance = metrics.findtext("distance")
                active_minutes = metrics.findtext("active-minutes")

                # Check if health metrics already exist for this date
                existing = db.query(HealthMetrics).filter(
                    HealthMetrics.user_id == current_user.user_id,
                    HealthMetrics.date == record_date
                ).first()

                if existing:
                    # Update existing record
                    existing.heart_rate = heart_rate or existing.heart_rate
                    existing.calories = calories or existing.calories
                    existing.resting_hr = resting_hr or existing.resting_hr
                    existing.spo2 = spo2 or existing.spo2
                    existing.sleep_quality = sleep_quality or existing.sleep_quality
                    if steps: existing.steps = int(steps)
                    if distance: existing.distance = float(distance)
                    if active_minutes: existing.active_minutes = int(active_minutes)
                else:
                    # Create new health metrics record
                    health_record = HealthMetrics(
                        user_id=current_user.user_id,
                        date=record_date,
                        heart_rate=heart_rate if heart_rate > 0 else None,
                        calories=calories if calories > 0 else None,
                        resting_hr=resting_hr if resting_hr > 0 else None,
                        spo2=spo2 if spo2 > 0 else None,
                        sleep_quality=sleep_quality if sleep_quality > 0 else None,
                        steps=int(steps) if steps else None,
                        distance=float(distance) if distance else None,
                        active_minutes=int(active_minutes) if active_minutes else None
                    )
                    db.add(health_record)
                imported += 1

        except Exception as e:
            errors.append(f"Error processing health data: {e}")
    else:
        # Handle exercise session data (existing logic)
        for i, row in enumerate(rows):
            try:
                exercise_type = str(row.get("exercise_type", "")).strip().lower()
                # Accept Vietnamese names too
                exercise_type = EXERCISE_NAME_MAPPING.get(exercise_type, exercise_type)
                if exercise_type not in VALID_EXERCISE_TYPES:
                    errors.append(f"Dòng {i+1}: exercise_type '{exercise_type}' không hợp lệ")
                    continue

                reps = int(row.get("reps_completed", 0) or 0)
                duration = int(row.get("duration_seconds", 0) or 0)
                accuracy = float(row.get("accuracy_score", 0) or 0)
                feedback = str(row.get("feedback", "") or "")

                # Parse date — accept ISO strings or date-only strings
                raw_date = str(row.get("date", "")).strip()
                try:
                    session_time = _dt.fromisoformat(raw_date) if raw_date else _dt.utcnow()
                except ValueError:
                    session_time = _dt.utcnow()

                # Create session
                session = WorkoutSession(
                    user_id=current_user.user_id,
                    start_time=session_time,
                    end_time=session_time,
                    status="completed"
                )
                db.add(session)
                db.flush()

                # Create detail
                detail = SessionDetail(
                    session_id=session.session_id,
                    exercise_type=exercise_type,
                    reps_completed=reps,
                    duration_seconds=duration,
                    accuracy_score=accuracy,
                    feedback=feedback,
                    completed_at=session_time
                )
                db.add(detail)
                imported += 1

            except Exception as e:
                errors.append(f"Dòng {i+1}: {e}")

    db.commit()

    return {
        "imported": imported,
        "total": len(rows) if not is_health_data else len(root.findall("metrics")),
        "errors": errors[:10]  # cap error list
    }
