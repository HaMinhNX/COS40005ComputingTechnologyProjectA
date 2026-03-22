import time
from typing import List, Dict, Optional, Tuple, Any
from .base import BaseExerciseStrategy
from ..common import ShoulderFlexionState, FeedbackPriority

class ShoulderFlexionStrategy(BaseExerciseStrategy):
    def __init__(self):
        super().__init__()
        self.state = ShoulderFlexionState.IDLE
        self.flex_start_threshold = 15
        self.flex_up_threshold = 145
        self.flex_down_threshold = 30
        
        self.left_arm_state = ShoulderFlexionState.IDLE
        self.right_arm_state = ShoulderFlexionState.IDLE
        self.left_arm_enter_time: Optional[float] = None
        self.right_arm_enter_time: Optional[float] = None
        self.left_arm_valid = True
        self.right_arm_valid = True
        self.left_arm_straight_valid = True
        self.right_arm_straight_valid = True
        self.left_elbow_angles = []
        self.right_elbow_angles = []
        
        self.thresholds = {
            'shoulder_flex_not_high_enough': 105,
            'shoulder_flex_elbow_not_straight': 165,
            'shoulder_flex_body_swing': 30,
        }

    def _process_single_arm_flexion(
        self, flexion_angle: Optional[float], elbow_angle: Optional[float],
        arm_state: int, arm_enter_time: Optional[float], arm_valid: bool,
        arm_straight_valid: bool, elbow_angles_list: List[float], arm_name: str
    ) -> Tuple[int, Optional[float], bool, bool, List[float]]:
        if flexion_angle is None:
            return arm_state, arm_enter_time, arm_valid, arm_straight_valid, elbow_angles_list
            
        if arm_state in [ShoulderFlexionState.FLEXION_START, ShoulderFlexionState.FLEXION_UP, ShoulderFlexionState.FLEXION_DOWN]:
            if elbow_angle is not None:
                elbow_angles_list.append(elbow_angle)
                if len(elbow_angles_list) > 3: elbow_angles_list.pop(0)
                avg_elbow = sum(elbow_angles_list) / len(elbow_angles_list)
                if avg_elbow < self.thresholds['shoulder_flex_elbow_not_straight']:
                    self.feedback_manager.add_feedback(f"Thẳng tay {arm_name} ra!", FeedbackPriority.MEDIUM)
                    arm_straight_valid = False
                else:
                    arm_straight_valid = True
                    
        # State transitions
        if arm_state == ShoulderFlexionState.IDLE and flexion_angle > self.flex_start_threshold:
            arm_state = ShoulderFlexionState.FLEXION_START
            arm_enter_time = time.time()
            arm_valid = True
            arm_straight_valid = True
            elbow_angles_list = []
            self.feedback_manager.start_new_rep()
        elif arm_state == ShoulderFlexionState.FLEXION_START and flexion_angle > self.flex_up_threshold:
            arm_state = ShoulderFlexionState.FLEXION_UP
            arm_enter_time = time.time()
        elif arm_state == ShoulderFlexionState.FLEXION_UP and flexion_angle < 70:
            arm_state = ShoulderFlexionState.FLEXION_DOWN
            arm_enter_time = time.time()
        elif arm_state == ShoulderFlexionState.FLEXION_DOWN and flexion_angle < self.flex_down_threshold:
            if arm_valid and arm_straight_valid:
                self.counter += 1
                self.feedback_manager.complete_rep()
            arm_state = ShoulderFlexionState.IDLE
            arm_enter_time = None
            elbow_angles_list = []
            
        return arm_state, arm_enter_time, arm_valid, arm_straight_valid, elbow_angles_list

    def process(self, landmarks: List[Any], angles: Dict[str, Any]) -> Tuple[int, List[str]]:
        left_flexion_angle = angles.get('left_flexion_angle')
        right_flexion_angle = angles.get('right_flexion_angle')
        left_elbow_angle = angles.get('left_elbow_angle')
        right_elbow_angle = angles.get('right_elbow_angle')
        hip_shoulder_angle = angles.get('hip_shoulder_angle')
        
        # Process left arm
        (self.left_arm_state, self.left_arm_enter_time, self.left_arm_valid, 
         self.left_arm_straight_valid, self.left_elbow_angles) = self._process_single_arm_flexion(
            left_flexion_angle, left_elbow_angle, self.left_arm_state, 
            self.left_arm_enter_time, self.left_arm_valid, self.left_arm_straight_valid,
            self.left_elbow_angles, "left"
        )
        
        # Process right arm
        (self.right_arm_state, self.right_arm_enter_time, self.right_arm_valid, 
         self.right_arm_straight_valid, self.right_elbow_angles) = self._process_single_arm_flexion(
            right_flexion_angle, right_elbow_angle, self.right_arm_state, 
            self.right_arm_enter_time, self.right_arm_valid, self.right_arm_straight_valid,
            self.right_elbow_angles, "right"
        )
        
        # Determine active state for display
        active_state = ShoulderFlexionState.IDLE
        if left_flexion_angle is not None and right_flexion_angle is not None:
            active_state = self.left_arm_state if left_flexion_angle > right_flexion_angle else self.right_arm_state
        elif left_flexion_angle is not None:
            active_state = self.left_arm_state
        elif right_flexion_angle is not None:
            active_state = self.right_arm_state
            
        self.state = active_state # Track active state
        
        if hip_shoulder_angle is not None and hip_shoulder_angle > self.thresholds['shoulder_flex_body_swing']:
            self.feedback_manager.add_feedback("Thẳng lưng lên", FeedbackPriority.LOW)
            
        return self.state, self.feedback_manager.get_feedback()

    def reset(self):
        super().reset()
        self.state = ShoulderFlexionState.IDLE
        self.left_arm_state = ShoulderFlexionState.IDLE
        self.right_arm_state = ShoulderFlexionState.IDLE
        self.left_arm_enter_time = None
        self.right_arm_enter_time = None
        self.left_arm_valid = True
        self.right_arm_valid = True
        self.left_arm_straight_valid = True
        self.right_arm_straight_valid = True
        self.left_elbow_angles = []
        self.right_elbow_angles = []
