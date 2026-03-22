import time
from typing import List, Dict, Optional, Tuple, Any
from .base import BaseExerciseStrategy
from ..common import SquatState, FeedbackPriority
from ..utils import AngleCalculator

class SquatStrategy(BaseExerciseStrategy):
    def __init__(self):
        super().__init__()
        self.state = SquatState.IDLE
        self.start_threshold = 160
        self.squat_threshold = 95
        self.symmetry_threshold = 125
        self.min_hold_time = 0.2
        self.hip_angle_threshold = 130
        self.min_hip_fold = 150
        self.hip_drop_threshold = 0.10
        
        self.squat_start_hip_y: Optional[float] = None
        self.squat_down_hip_y: Optional[float] = None
        self.state_enter_time: Optional[float] = None
        self.pending_rep_valid = True
        
        self.thresholds = {
            'squat_not_deep_enough': 90,
            'squat_too_deep': 60,
            'squat_forward_bend_too_little': 5,
            'squat_forward_bend_too_much': 60,
            'squat_knee_forward_max': 0.06,
            'squat_knee_valgus_min_ratio': 0.70,
        }

    def process(self, landmarks: List[Any], angles: Dict[str, Any]) -> Tuple[int, List[str]]:
        left_hip = landmarks[23]; right_hip = landmarks[24]
        left_knee = landmarks[25]; right_knee = landmarks[26]
        left_ankle = landmarks[27]; right_ankle = landmarks[28]
        left_shoulder = landmarks[11]; right_shoulder = landmarks[12]
        
        knee_angle = angles.get('knee_angle_avg')
        back_angle = angles.get('back_angle')
        
        # Calculate individual knee angles for symmetry
        left_knee_angle = AngleCalculator.calculate_knee_angle(left_hip, left_knee, left_ankle, vt=0.7)
        right_knee_angle = AngleCalculator.calculate_knee_angle(right_hip, right_knee, right_ankle, vt=0.7)
        
        effective_knee_avg = knee_angle
        
        # Calculate hip angles
        left_hip_angle = None
        if all(p.visibility > 0.6 for p in [left_shoulder, left_hip, left_knee]):
            left_hip_angle = AngleCalculator.calculate_angle(left_shoulder, left_hip, left_knee)
        
        right_hip_angle = None
        if all(p.visibility > 0.6 for p in [right_shoulder, right_hip, right_knee]):
            right_hip_angle = AngleCalculator.calculate_angle(right_shoulder, right_hip, right_knee)
        
        hip_angle_avg = None
        if left_hip_angle is not None and right_hip_angle is not None:
            hip_angle_avg = (left_hip_angle + right_hip_angle) / 2
        elif left_hip_angle is not None:
            hip_angle_avg = left_hip_angle
        elif right_hip_angle is not None:
            hip_angle_avg = right_hip_angle
            
        current_hip_y_avg = (left_hip.y + right_hip.y) / 2
        
        if effective_knee_avg is None:
            return self.state, self.feedback_manager.get_feedback()
            
        visible_knees = []
        if left_knee_angle is not None: visible_knees.append(left_knee_angle)
        if right_knee_angle is not None: visible_knees.append(right_knee_angle)
        
        if not visible_knees and hip_angle_avg is None:
            return self.state, self.feedback_manager.get_feedback()
            
        knee_diff = abs(visible_knees[0] - visible_knees[1]) if len(visible_knees) == 2 else 0
        
        # Feedback: Depth
        if self.state == SquatState.SQUAT_DOWN:
            if effective_knee_avg > self.squat_threshold + 10:
                self.feedback_manager.add_feedback("Xuống sâu hơn", FeedbackPriority.MEDIUM)
            elif effective_knee_avg < 60:
                self.feedback_manager.add_feedback("Quá sâu", FeedbackPriority.MEDIUM)
            
            if hip_angle_avg is not None and hip_angle_avg > self.min_hip_fold:
                self.feedback_manager.add_feedback("Gập hông sâu hơn!", FeedbackPriority.HIGH)
        
        # State transitions
        if self.state == SquatState.IDLE and effective_knee_avg > self.start_threshold:
            self.state = SquatState.SQUAT_START
            self.state_enter_time = time.time()
            self.squat_start_hip_y = current_hip_y_avg
            self.squat_down_hip_y = None
            self.pending_rep_valid = True
            self.feedback_manager.start_new_rep()
            
        elif self.state == SquatState.SQUAT_START and effective_knee_avg < self.squat_threshold:
            if self.state_enter_time is not None:
                duration = time.time() - self.state_enter_time
                if duration < 0.05: # Fast movement check
                    self.pending_rep_valid = False
            
            symmetry_ok = False
            if len(visible_knees) == 2:
                symmetry_ok = (visible_knees[0] < self.symmetry_threshold and visible_knees[1] < self.symmetry_threshold) or knee_diff < 30
            elif len(visible_knees) == 1:
                symmetry_ok = visible_knees[0] < self.squat_threshold
            else:
                symmetry_ok = True
                
            if symmetry_ok:
                if hip_angle_avg is not None and hip_angle_avg < self.hip_angle_threshold:
                    self.state = SquatState.SQUAT_DOWN
                    self.state_enter_time = time.time()
                    self.squat_down_hip_y = current_hip_y_avg
                else:
                    if hip_angle_avg is not None:
                        self.feedback_manager.add_feedback("Deeper hip bend!", FeedbackPriority.HIGH)
                    self.pending_rep_valid = False
            else:
                self.feedback_manager.add_feedback("Even squat", FeedbackPriority.MEDIUM)
                self.pending_rep_valid = False
                
        elif self.state == SquatState.SQUAT_DOWN:
            # Hip y at down entry
            if self.squat_down_hip_y is None:
                self.squat_down_hip_y = current_hip_y_avg
            else:
                self.squat_down_hip_y = max(self.squat_down_hip_y, current_hip_y_avg)
                
            if effective_knee_avg > self.start_threshold:
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if duration >= self.min_hold_time:
                        actual_drop = 0.0
                        if self.squat_down_hip_y is not None and self.squat_start_hip_y is not None:
                            actual_drop = self.squat_down_hip_y - self.squat_start_hip_y
                            
                        if actual_drop >= self.hip_drop_threshold:
                            if hip_angle_avg is not None and hip_angle_avg <= self.hip_angle_threshold:
                                if self.pending_rep_valid:
                                    self.counter += 1
                                    self.feedback_manager.complete_rep()
                        else:
                            self.feedback_manager.add_feedback("Lower hips!", FeedbackPriority.MEDIUM)
                    else:
                         self.feedback_manager.add_feedback(f"Hold longer ({self.min_hold_time}s)", FeedbackPriority.LOW)
                         return self.state, self.feedback_manager.get_feedback()

                self.pending_rep_valid = True
                self.state = SquatState.SQUAT_START
                self.squat_start_hip_y = current_hip_y_avg
                self.squat_down_hip_y = None
                self.state_enter_time = None
                self.feedback_manager.start_new_rep()
                
        # Feedback back angle
        if back_angle is not None and self.state in [SquatState.SQUAT_START, SquatState.SQUAT_DOWN]:
            if back_angle < self.thresholds['squat_forward_bend_too_little']:
                self.feedback_manager.add_feedback("Lean forward", FeedbackPriority.MEDIUM)
            elif back_angle > self.thresholds['squat_forward_bend_too_much']:
                self.feedback_manager.add_feedback("Less lean", FeedbackPriority.MEDIUM)

        return self.state, self.feedback_manager.get_feedback()

    def reset(self):
        super().reset()
        self.state = SquatState.IDLE
        self.squat_start_hip_y = None
        self.squat_down_hip_y = None
        self.state_enter_time = None
        self.pending_rep_valid = True
