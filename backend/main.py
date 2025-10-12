from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Import the logic classes and global counter instance
from exercise_logic import (
    AngleCalculator, 
    Landmark, 
    EXERCISE_COUNTER, 
    SquatState, 
    BicepCurlState
)

app = FastAPI()

# --- Helper to get state name from value ---
def get_state_name(state_class, state_value):
    state_dict = {v: k for k, v in state_class.__dict__.items() if isinstance(v, int)}
    return state_dict.get(state_value, "UNKNOWN")

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas for API ---
class LandmarkData(BaseModel):
    x: float = Field(..., ge=0, le=1) 
    y: float = Field(..., ge=0, le=1)
    z: float = Field(default=0)
    visibility: float = Field(default=0)

class ProcessRequest(BaseModel):
    landmarks: List[LandmarkData]
    current_exercise: str

class ProcessResponse(BaseModel):
    squat_count: int
    curl_count: int
    total_reps: int
    squat_state_name: str
    curl_state_name: str
    feedback: str

# --- Helper Function to calculate all angles ---
def calculate_all_angles(landmarks: List[LandmarkData]) -> Dict[str, Any]:
    lm_objects = [Landmark(lm.x, lm.y, lm.z, lm.visibility) for lm in landmarks]

    if len(lm_objects) < 33:
        return {'error': 'Insufficient landmarks'}

    # Get all required landmarks
    left_shoulder = lm_objects[11]
    left_elbow = lm_objects[13]
    left_wrist = lm_objects[15]
    left_hip = lm_objects[23]
    left_knee = lm_objects[25]
    left_ankle = lm_objects[27]
    
    right_shoulder = lm_objects[12]
    right_elbow = lm_objects[14]
    right_wrist = lm_objects[16]
    right_hip = lm_objects[24]
    right_knee = lm_objects[26]
    right_ankle = lm_objects[28]

    # Calculate bicep angles for BOTH arms
    left_bicep_angle = AngleCalculator.calculate_bicep_angle(
        left_shoulder, left_elbow, left_wrist, visibility_threshold=0.7
    )
    right_bicep_angle = AngleCalculator.calculate_bicep_angle(
        right_shoulder, right_elbow, right_wrist, visibility_threshold=0.7
    )
    
    # Elbow-Torso Angle
    elbow_torso_result = AngleCalculator.calculate_elbow_torso_angle(
        left_hip, left_shoulder, left_elbow, 
        right_hip, right_shoulder, right_elbow, 
        visibility_threshold=0.7
    )
    
    # Hip-Shoulder Angle (use left as primary)
    hip_shoulder_angle = AngleCalculator.calculate_hip_shoulder_angle(
        left_hip, left_shoulder, visibility_threshold=0.7
    )

    # Knee Angle (average)
    knee_angle_avg = AngleCalculator.calculate_average_knee_angle(
        left_hip, left_knee, left_ankle, 
        right_hip, right_knee, right_ankle, 
        visibility_threshold=0.7
    )
    
    # Back Angle (average)
    left_back_angle = AngleCalculator.calculate_hip_shoulder_angle(
        left_hip, left_shoulder, visibility_threshold=0.7
    )
    right_back_angle = AngleCalculator.calculate_hip_shoulder_angle(
        right_hip, right_shoulder, visibility_threshold=0.7
    )
    
    back_angle = None
    if left_back_angle is not None and right_back_angle is not None:
        back_angle = (left_back_angle + right_back_angle) / 2
    elif left_back_angle is not None:
        back_angle = left_back_angle
    elif right_back_angle is not None:
        back_angle = right_back_angle

    return {
        'left_bicep_angle': left_bicep_angle,
        'right_bicep_angle': right_bicep_angle,
        'elbow_torso_result': elbow_torso_result,
        'hip_shoulder_angle': hip_shoulder_angle,
        'knee_angle_avg': knee_angle_avg,
        'back_angle': back_angle,
        'landmarks': lm_objects
    }


# --- API Endpoints ---
@app.post("/select_exercise")
async def select_exercise(exercise_name: str):
    """Resets the counter state for a specific exercise."""
    EXERCISE_COUNTER.reset_state(exercise_name)
    return {"message": f"State reset for {exercise_name}"}


@app.post("/process_landmarks", response_model=ProcessResponse)
async def process_landmarks_api(request: ProcessRequest):
    """Receives landmarks and processes the exercise logic."""
    if not request.landmarks:
        raise HTTPException(status_code=400, detail="No landmarks provided")

    angles = calculate_all_angles(request.landmarks)
    
    if 'error' in angles:
        raise HTTPException(status_code=400, detail=angles['error'])

    # Extract landmark objects
    lm_objects = angles['landmarks']
    
    # Get required landmarks
    left_shoulder = lm_objects[11]
    left_elbow = lm_objects[13]
    left_wrist = lm_objects[15]
    left_hip = lm_objects[23]
    left_knee = lm_objects[25]
    left_ankle = lm_objects[27]
    
    right_shoulder = lm_objects[12]
    right_elbow = lm_objects[14]
    right_wrist = lm_objects[16]
    right_hip = lm_objects[24]
    right_knee = lm_objects[26]
    right_ankle = lm_objects[28]

    state = None
    feedbacks = []
    
    # Process exercise logic
    if request.current_exercise == 'bicep-curl':
        # FIXED: Pass all required parameters with correct names
        state, feedbacks = EXERCISE_COUNTER.process_bicep_curl(
            left_shoulder=left_shoulder,
            left_elbow=left_elbow,
            left_wrist=left_wrist,
            left_hip=left_hip,
            right_shoulder=right_shoulder,
            right_elbow=right_elbow,
            right_wrist=right_wrist,
            right_hip=right_hip,
            left_bicep_angle=angles['left_bicep_angle'],
            right_bicep_angle=angles['right_bicep_angle'],
            elbow_torso_result=angles['elbow_torso_result'],
            hip_shoulder_angle=angles['hip_shoulder_angle']
        )
        curl_state_name = get_state_name(BicepCurlState, state)
        squat_state_name = get_state_name(SquatState, EXERCISE_COUNTER.squat_state)

    elif request.current_exercise == 'squat':
        state, feedbacks = EXERCISE_COUNTER.process_squat(
            knee_angle=angles['knee_angle_avg'], 
            back_angle=angles['back_angle'], 
            left_hip=left_hip,
            right_hip=right_hip, 
            left_knee=left_knee,
            right_knee=right_knee, 
            left_ankle=left_ankle,
            right_ankle=right_ankle
        )
        squat_state_name = get_state_name(SquatState, state)
        curl_state_name = get_state_name(BicepCurlState, EXERCISE_COUNTER.bicep_curl_state)

    else:
        curl_state_name = get_state_name(BicepCurlState, EXERCISE_COUNTER.bicep_curl_state)
        squat_state_name = get_state_name(SquatState, EXERCISE_COUNTER.squat_state)

    # Create feedback string
    default_feedback = "TỐT LẮM, TIẾP TỤC PHÁT HUY!"
    feedback_string = ", ".join(feedbacks) if feedbacks else default_feedback

    # Return result
    return ProcessResponse(
        squat_count=EXERCISE_COUNTER.squat_counter,
        curl_count=EXERCISE_COUNTER.curl_counter,
        total_reps=EXERCISE_COUNTER.total_reps,
        squat_state_name=squat_state_name,
        curl_state_name=curl_state_name,
        feedback=feedback_string
    )

# To run: uvicorn main:app --reload