import time
from typing import List, Dict, Optional, Tuple, Any
from .base import BaseExerciseStrategy
from ..common import KneeRaiseState

class KneeRaiseStrategy(BaseExerciseStrategy):
    def __init__(self):
        super().__init__()
        self.state = KneeRaiseState.IDLE
        self.knee_raise_leg_threshold = 140
        self.knee_raise_arm_threshold = 80
        self.knee_raise_start_leg_threshold = 150
        self.knee_raise_start_arm_threshold = 30
        
        self.active_pair_side: Optional[str] = None
        self.pair_enter_time: Optional[float] = None
        self.pair_valid = True
        self.pair_sync_valid = True
        
        self.recent_leg_angles = {'left': [], 'right': []}
        self.recent_arm_angles = {'left': [], 'right': []}
        
        self.thresholds = {
            'knee_raise_leg_not_high_enough': 150,
            'knee_raise_arm_not_high_enough': 60,
            'knee_raise_body_swing': 25,
            'knee_raise_sync_delay_max': 0.8,
            'knee_raise_max_hip_tilt': 0.15,
        }

    def _average_recent_angles(self, angles_list: List[float]) -> Optional[float]:
        if angles_list: return sum(angles_list) / len(angles_list)
        return None

    def process(self, landmarks: List[Any], angles: Dict[str, Any]) -> Tuple[int, List[str]]:
        left_hip = landmarks[23]; right_hip = landmarks[24]
        left_knee_angle = angles.get('left_knee_angle')
        right_knee_angle = angles.get('right_knee_angle')
        left_flexion_angle = angles.get('left_flexion_angle')
        right_flexion_angle = angles.get('right_flexion_angle')
        hip_shoulder_angle = angles.get('hip_shoulder_angle')
        
        # Simple smoothing
        if left_knee_angle is not None:
            self.recent_leg_angles['left'].append(left_knee_angle)
            if len(self.recent_leg_angles['left']) > 2: self.recent_leg_angles['left'].pop(0)
        if right_knee_angle is not None:
            self.recent_leg_angles['right'].append(right_knee_angle)
            if len(self.recent_leg_angles['right']) > 2: self.recent_leg_angles['right'].pop(0)
            
        avg_left_knee = self._average_recent_angles(self.recent_leg_angles['left']) or left_knee_angle
        avg_right_knee = self._average_recent_angles(self.recent_leg_angles['right']) or right_knee_angle
        
        # Determine active pair
        active_pair = None
        if avg_left_knee is not None and avg_right_knee is not None:
            active_pair = 'left_leg_right_arm' if avg_left_knee < avg_right_knee else 'right_leg_left_arm'
        elif avg_left_knee is not None: active_pair = 'left_leg_right_arm'
        elif avg_right_knee is not None: active_pair = 'right_leg_left_arm'
        
        self.active_pair_side = active_pair
        
        if active_pair and avg_left_knee is not None and avg_right_knee is not None and left_flexion_angle is not None and right_flexion_angle is not None:
            leg_angle = avg_left_knee if active_pair == 'left_leg_right_arm' else avg_right_knee
            arm_angle = right_flexion_angle if active_pair == 'left_leg_right_arm' else left_flexion_angle
            
            # State transitions
            if self.state == KneeRaiseState.IDLE:
                if leg_angle > self.knee_raise_start_leg_threshold and arm_angle < self.knee_raise_start_arm_threshold:
                    self.state = KneeRaiseState.RAISE_START
                    self.pair_enter_time = time.time()
                    self.pair_valid = True
                    self.feedback_manager.start_new_rep()
            elif self.state == KneeRaiseState.RAISE_START:
                if leg_angle < self.knee_raise_leg_threshold and arm_angle > self.knee_raise_arm_threshold:
                    self.state = KneeRaiseState.RAISE_UP
                    self.pair_enter_time = time.time()
            elif self.state == KneeRaiseState.RAISE_UP:
                if leg_angle > self.knee_raise_start_leg_threshold and arm_angle < self.knee_raise_start_arm_threshold:
                    if self.pair_valid:
                        self.counter += 1
                        self.feedback_manager.complete_rep()
                    self.state = KneeRaiseState.IDLE
                    self.pair_enter_time = None
                    
        return self.state, self.feedback_manager.get_feedback()

    def reset(self):
        super().reset()
        self.state = KneeRaiseState.IDLE
        self.active_pair_side = None
        self.pair_enter_time = None
        self.pair_valid = True
        self.pair_sync_valid = True
        self.recent_leg_angles = {'left': [], 'right': []}
        self.recent_arm_angles = {'left': [], 'right': []}
