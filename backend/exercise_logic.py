"""
Backward compatibility facade for exercise logic.
This file now delegates to the modular implementation in logic/ directory.
"""
from typing import List, Dict, Any
from logic.common import (
    Landmark
)
from logic.utils import AngleCalculator
from logic.counter import ExerciseCounter

# Create global instance for backward compatibility
EXERCISE_COUNTER = ExerciseCounter()

# Maintain the prev_reps global variable
prev_reps = {
    'squat': 0,
    'bicep-curl': 0,
    'shoulder-flexion': 0,
    'knee-raise': 0
}

# Delegate calculate_all_angles to AngleCalculator or keep here for convenience
def calculate_all_angles(landmarks: List[Landmark]) -> Dict[str, Any]:
    # This is a bit of a duplicate but keeps the API stable
    if len(landmarks) < 33:
        return {'error': 'Not enough landmarks detected'}
        
    left_shoulder = landmarks[11]; right_shoulder = landmarks[12]
    left_elbow = landmarks[13]; right_elbow = landmarks[14]
    left_wrist = landmarks[15]; right_wrist = landmarks[16]
    left_hip = landmarks[23]; right_hip = landmarks[24]
    left_knee = landmarks[25]; right_knee = landmarks[26]
    left_ankle = landmarks[27]; right_ankle = landmarks[28]

    angles = {}
    angles['knee_angle_avg'] = AngleCalculator.calculate_average_knee_angle(
        left_hip, left_knee, left_ankle, right_hip, right_knee, right_ankle
    )
    
    # Simple back angle calculation
    mid_hip = [(left_hip.x + right_hip.x) / 2, (left_hip.y + right_hip.y) / 2]
    mid_shoulder = [(left_shoulder.x + right_shoulder.x) / 2, (left_shoulder.y + right_shoulder.y) / 2]
    angles['back_angle'] = AngleCalculator.calculate_vertical_angle(mid_hip, mid_shoulder)
    
    angles['left_bicep_angle'] = AngleCalculator.calculate_bicep_angle(left_shoulder, left_elbow, left_wrist)
    angles['right_bicep_angle'] = AngleCalculator.calculate_bicep_angle(right_shoulder, right_elbow, right_wrist)
    
    angles['elbow_torso_result'] = AngleCalculator.calculate_elbow_torso_angle(
        left_hip, left_shoulder, left_elbow, right_hip, right_shoulder, right_elbow
    )
    
    angles['hip_shoulder_angle'] = AngleCalculator.calculate_hip_shoulder_angle(left_hip, left_shoulder)

    angles['left_flexion_angle'] = AngleCalculator.calculate_shoulder_flexion_angle(left_hip, left_shoulder, left_wrist)
    angles['right_flexion_angle'] = AngleCalculator.calculate_shoulder_flexion_angle(right_hip, right_shoulder, right_wrist)
    
    angles['left_elbow_angle'] = AngleCalculator.calculate_elbow_bend_angle(left_shoulder, left_elbow, left_wrist)
    angles['right_elbow_angle'] = AngleCalculator.calculate_elbow_bend_angle(right_shoulder, right_elbow, right_wrist)
    
    angles['left_knee_angle'] = AngleCalculator.calculate_knee_angle(left_hip, left_knee, left_ankle)
    angles['right_knee_angle'] = AngleCalculator.calculate_knee_angle(right_hip, right_knee, right_ankle)

    return angles