import time
from typing import List, Dict, Optional, Tuple, Any
from .base import BaseExerciseStrategy
from ..common import BicepCurlState, FeedbackPriority
from ..utils import AngleCalculator

class BicepCurlStrategy(BaseExerciseStrategy):
    def __init__(self):
        super().__init__()
        self.state = BicepCurlState.IDLE
        self.curl_start_threshold = 162
        self.curl_up_threshold = 60
        self.curl_down_threshold = 162
        
        self.curl_start_shoulder: Optional[Dict[str, float]] = None
        self.elbow_position_valid = True
        self.pending_rep_valid = True
        self.state_enter_time: Optional[float] = None
        self.active_arm_side: Optional[str] = None
        
        self.min_concentric_time = 0.5
        self.min_eccentric_time = 1.0
        
        self.thresholds = {
            'bicep_curl_not_high_enough': 70,
            'bicep_curl_not_low_enough': 162,
            'bicep_curl_body_swing': 30,
            'bicep_curl_shoulder_movement': 0.15,
            'bicep_curl_elbow_dev_max': 25,
        }

    def process(self, landmarks: List[Any], angles: Dict[str, Any]) -> Tuple[int, List[str]]:
        left_shoulder = landmarks[11]; left_elbow = landmarks[13]; left_wrist = landmarks[15]; left_hip = landmarks[23]
        right_shoulder = landmarks[12]; right_elbow = landmarks[14]; right_wrist = landmarks[16]; right_hip = landmarks[24]
        
        left_bicep_angle = angles.get('left_bicep_angle')
        right_bicep_angle = angles.get('right_bicep_angle')
        elbow_torso_result = angles.get('elbow_torso_result')
        hip_shoulder_angle = angles.get('hip_shoulder_angle')
        
        left_elbow_torso = elbow_torso_result[0] if elbow_torso_result else None
        right_elbow_torso = elbow_torso_result[1] if elbow_torso_result else None

        active_bicep_angle = None
        active_side = None
        active_elbow_torso = None
        active_shoulder = None
        
        if left_bicep_angle is not None and right_bicep_angle is not None:
            if left_bicep_angle < right_bicep_angle:
                active_bicep_angle = left_bicep_angle
                active_side = 'left'
                active_elbow_torso = left_elbow_torso
                active_shoulder = left_shoulder
            else:
                active_bicep_angle = right_bicep_angle
                active_side = 'right'
                active_elbow_torso = right_elbow_torso
                active_shoulder = right_shoulder
        elif left_bicep_angle is not None:
            active_bicep_angle = left_bicep_angle
            active_side = 'left'
            active_elbow_torso = left_elbow_torso
            active_shoulder = left_shoulder
        elif right_bicep_angle is not None:
            active_bicep_angle = right_bicep_angle
            active_side = 'right'
            active_elbow_torso = right_elbow_torso
            active_shoulder = right_shoulder

        if self.active_arm_side != active_side:
            self.active_arm_side = active_side

        if active_bicep_angle is not None:
            if (self.state in [BicepCurlState.IDLE, BicepCurlState.CURL_START]) and active_bicep_angle < self.thresholds['bicep_curl_not_low_enough']:
                self.feedback_manager.add_feedback("Duỗi thẳng tay", FeedbackPriority.MEDIUM)
            
            if self.state == BicepCurlState.CURL_UP and active_bicep_angle > self.thresholds['bicep_curl_not_high_enough']:
                self.feedback_manager.add_feedback("Gập cao hơn", FeedbackPriority.MEDIUM)

            if self.state in [BicepCurlState.CURL_START, BicepCurlState.CURL_UP]:
                if active_elbow_torso is not None and active_elbow_torso > self.thresholds['bicep_curl_elbow_dev_max']:
                    self.feedback_manager.add_feedback("Khép khuỷu tay lại!", FeedbackPriority.HIGH)
                    self.elbow_position_valid = False

            if self.state == BicepCurlState.IDLE and active_bicep_angle > self.curl_start_threshold:
                self.state = BicepCurlState.CURL_START
                self.state_enter_time = time.time()
                self.elbow_position_valid = True
                self.feedback_manager.start_new_rep()
                
            elif self.state == BicepCurlState.CURL_START and active_bicep_angle < self.curl_up_threshold:
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if duration < self.min_concentric_time:
                        self.feedback_manager.add_feedback("Lên chậm thôi", FeedbackPriority.HIGH)
                        self.pending_rep_valid = False
                
                self.state = BicepCurlState.CURL_UP
                self.state_enter_time = time.time()
                self.curl_start_shoulder = {'x': active_shoulder.x, 'y': active_shoulder.y} if active_shoulder else None
                
            elif self.state == BicepCurlState.CURL_UP and active_bicep_angle > self.curl_down_threshold:
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if duration < self.min_eccentric_time:
                        self.feedback_manager.add_feedback("Xuống chậm thôi", FeedbackPriority.HIGH)
                        self.pending_rep_valid = False
                
                if self.pending_rep_valid and self.elbow_position_valid:
                    self.counter += 1
                    self.feedback_manager.complete_rep()
                
                self.pending_rep_valid = True
                self.elbow_position_valid = True
                self.state = BicepCurlState.CURL_START
                self.curl_start_shoulder = None
                self.state_enter_time = None
                self.feedback_manager.start_new_rep()

        if hip_shoulder_angle is not None and hip_shoulder_angle > self.thresholds['bicep_curl_body_swing']:
            self.feedback_manager.add_feedback("Đừng đung đưa người", FeedbackPriority.MEDIUM)
        
        if self.state == BicepCurlState.CURL_UP and self.curl_start_shoulder is not None and active_shoulder is not None:
            dist = AngleCalculator.find_distance(active_shoulder.x, active_shoulder.y, 
                                                self.curl_start_shoulder['x'], self.curl_start_shoulder['y'])
            if dist > self.thresholds['bicep_curl_shoulder_movement']:
                self.feedback_manager.add_feedback("Giữ vai cố định", FeedbackPriority.MEDIUM)

        return self.state, self.feedback_manager.get_feedback()

    def reset(self):
        super().reset()
        self.state = BicepCurlState.IDLE
        self.curl_start_shoulder = None
        self.elbow_position_valid = True
        self.pending_rep_valid = True
        self.state_enter_time = None
        self.active_arm_side = None
