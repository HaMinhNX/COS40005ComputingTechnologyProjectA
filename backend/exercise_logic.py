# V2/medic1/backend/exercise_logic.py
import math
import time
from typing import List, Dict, Optional, Tuple, Any

def get_state_name(state_class, state_value):
    state_dict = {v: k for k, v in state_class.__dict__.items() if isinstance(v, int)}
    return state_dict.get(state_value, "UNKNOWN")
# --- Enums and Constants ---
class SquatState:
    IDLE = 0
    SQUAT_START = 1
    SQUAT_DOWN = 2
    SQUAT_HOLD = 3
    SQUAT_UP = 4

class BicepCurlState:
    IDLE = 0
    CURL_START = 1
    CURL_UP = 2
    CURL_HOLD = 3
    CURL_DOWN = 4

class ShoulderFlexionState:
    IDLE = 0
    FLEXION_START = 1      # Arm starting to raise
    FLEXION_UP = 2         # Arm raised overhead
    FLEXION_DOWN = 3       # Arm lowering back down

class KneeRaiseState:
    IDLE = 0
    RAISE_START = 1        # Starting the raise (leg and opposite arm beginning)
    RAISE_UP = 2           # Both leg knee and opposite arm at peak
    RAISE_DOWN = 3         # Lowering back down (simplified, count here)

class FeedbackPriority:
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# --- Data Structure for Landmark (used by Pydantic in main.py) ---
class Landmark:
    def __init__(self, x: float, y: float, z: float = 0, visibility: float = 0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

# --- FeedbackManager class ---
class FeedbackManager:
    def __init__(self, window_size: int = 5):
        self.feedback_window = []
        self.window_size = window_size
        self.current_feedback = []
        self.priority_queue = []
        self.rep_completed = False
        self.rep_summary = []

    def start_new_rep(self):
        self.feedback_window = []
        self.current_feedback = []
        self.priority_queue = []
        self.rep_completed = False
        self.rep_summary = []

    def complete_rep(self):
        self._process_feedback()
        high_pri = [self.priority_queue[0]['feedback']] if self.priority_queue else []
        frequent = list(self.current_feedback)
        
        all_feedback = list(set(high_pri + frequent))
        
        def sort_key(feedback):
            max_pri = FeedbackPriority.LOW
            for item in self.priority_queue:
                if item['feedback'] == feedback:
                    max_pri = max(max_pri, -item['priority'])
            return max_pri

        all_feedback.sort(key=sort_key, reverse=True)
        
        self.rep_summary = all_feedback[:2]
        self.rep_completed = True

    def add_feedback(self, feedback: str, priority: int):
        self.priority_queue.append({'priority': -priority, 'feedback': feedback})
        self.priority_queue.sort(key=lambda x: x['priority'])
        if len(self.priority_queue) > self.window_size * 2:
            self.priority_queue = self.priority_queue[:self.window_size * 2]
        self.feedback_window.append({'feedback': feedback, 'priority': priority})
        if len(self.feedback_window) > self.window_size:
            self.feedback_window.pop(0)
        self._process_feedback()

    def _process_feedback(self):
        feedback_count = {}
        for item in self.feedback_window:
            feedback = item['feedback']
            feedback_count[feedback] = feedback_count.get(feedback, 0) + 1
        
        threshold = math.floor(len(self.feedback_window) / 2)
        self.current_feedback = [key for key, count in feedback_count.items() if count > threshold]

    def get_feedback(self) -> List[str]:
        if self.rep_completed:
            return self.rep_summary
        else:
            return self.current_feedback

    def clear_feedback(self):
        self.feedback_window = []
        self.current_feedback = []
        self.priority_queue = []
        self.rep_completed = False
        self.rep_summary = []

# --- AngleCalculator class ---
class AngleCalculator:
    # PERFORMANCE: Cache constants
    RAD_TO_DEG = 180.0 / math.pi
    
    @staticmethod
    def calculate_angle(a: Landmark, b: Landmark, c: Landmark) -> float:
        """OPTIMIZED: Faster angle calculation with direct access"""
        # Direct access instead of list creation (faster)
        radians = math.atan2(c.y - b.y, c.x - b.x) - \
                  math.atan2(a.y - b.y, a.x - b.x)
        
        angle = abs(radians * AngleCalculator.RAD_TO_DEG)
        return angle if angle <= 180 else 360 - angle

    @staticmethod
    def calculate_vertical_angle(point1: List[float], point2: List[float]) -> float:
        """OPTIMIZED: Faster vertical angle calculation"""
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return abs(math.atan2(dx, -dy) * AngleCalculator.RAD_TO_DEG)

    @staticmethod
    def find_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """OPTIMIZED: Fast distance calculation"""
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def angle_deg(p1, pref, p2) -> float:
        def get_coords(p):
            if isinstance(p, Landmark):
                return [p.x, p.y]
            elif isinstance(p, (list, tuple)):
                return p[:2]
            return [0, 0]

        p1_coords = get_coords(p1)
        pref_coords = get_coords(pref)
        p2_coords = get_coords(p2)
        
        p1ref = [p1_coords[0] - pref_coords[0], p1_coords[1] - pref_coords[1]]
        p2ref = [p2_coords[0] - pref_coords[0], p2_coords[1] - pref_coords[1]]
        
        dot_product = p1ref[0] * p2ref[0] + p1ref[1] * p2ref[1]
        magnitude_p1ref = math.sqrt(p1ref[0]**2 + p1ref[1]**2)
        magnitude_p2ref = math.sqrt(p2ref[0]**2 + p2ref[1]**2)
        
        if magnitude_p1ref == 0 or magnitude_p2ref == 0:
            return 0.0
            
        cos_theta = dot_product / (magnitude_p1ref * magnitude_p2ref)
        cos_theta = max(-1, min(1, cos_theta))
        
        angle_rad = math.acos(cos_theta)
        return angle_rad * 180 / math.pi

    @staticmethod
    def calculate_elbow_torso_angle(
        left_hip: Landmark, left_shoulder: Landmark, left_elbow: Landmark, 
        right_hip: Landmark, right_shoulder: Landmark, right_elbow: Landmark, 
        visibility_threshold: float = 0.6
    ) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
        
        def is_visible(points):
            return all(p.visibility > visibility_threshold for p in points)

        left_points = [left_hip, left_shoulder, left_elbow]
        right_points = [right_hip, right_shoulder, right_elbow]
        left_visible = is_visible(left_points)
        right_visible = is_visible(right_points)
        
        left_angle: Optional[float] = None  
        right_angle: Optional[float] = None  
        
        if left_visible:
            left_angle = AngleCalculator.angle_deg(left_hip, left_shoulder, left_elbow)
        if right_visible:
            right_angle = AngleCalculator.angle_deg(right_hip, right_shoulder, right_elbow)

        if left_visible and right_visible:
            if left_angle is not None and right_angle is not None:
                avg_angle = (left_angle + right_angle) / 2
            else:
                avg_angle = 0.0
            return left_angle, right_angle, avg_angle, "front"
        elif left_visible:
            return left_angle, None, left_angle, "left_side"
        elif right_visible:
            return None, right_angle, right_angle, "right_side"
        else:
            return None, None, None, "unclear"

    @staticmethod
    def calculate_hip_shoulder_angle(hip: Landmark, shoulder: Landmark, visibility_threshold: float = 0.6) -> Optional[float]:
        if hip.visibility > visibility_threshold and shoulder.visibility > visibility_threshold:
            return AngleCalculator.calculate_vertical_angle([hip.x, hip.y], [shoulder.x, shoulder.y])
        return None

    @staticmethod
    def calculate_knee_angle(hip: Landmark, knee: Landmark, ankle: Landmark, visibility_threshold: float = 0.6) -> Optional[float]:
        is_visible = lambda p: p.visibility > visibility_threshold
        if is_visible(hip) and is_visible(knee) and is_visible(ankle):
            return AngleCalculator.calculate_angle(hip, knee, ankle)
        return None

    @staticmethod
    def calculate_average_knee_angle(
        left_hip: Landmark, left_knee: Landmark, left_ankle: Landmark, 
        right_hip: Landmark, right_knee: Landmark, right_ankle: Landmark, 
        visibility_threshold: float = 0.6
    ) -> Optional[float]:
        left_angle = AngleCalculator.calculate_knee_angle(left_hip, left_knee, left_ankle, visibility_threshold)
        right_angle = AngleCalculator.calculate_knee_angle(right_hip, right_knee, right_ankle, visibility_threshold)
        
        if left_angle is not None and right_angle is not None:
            return (left_angle + right_angle) / 2
        elif left_angle is not None:
            return left_angle
        elif right_angle is not None:
            return right_angle
        return None

    @staticmethod
    def calculate_bicep_angle(side_shoulder: Landmark, side_elbow: Landmark, side_wrist: Landmark, visibility_threshold: float = 0.6) -> Optional[float]:
        if all(p.visibility > visibility_threshold for p in [side_shoulder, side_elbow, side_wrist]):
            return AngleCalculator.calculate_angle(side_shoulder, side_elbow, side_wrist)
        return None

    @staticmethod
    def check_wrist_tuck(elbow: Landmark, wrist: Landmark, visibility_threshold: float = 0.6) -> bool:
        if elbow.visibility > visibility_threshold and wrist.visibility > visibility_threshold:
            return wrist.y > elbow.y + 0.05
        return False

    @staticmethod
    def calculate_shoulder_flexion_angle(hip: Landmark, shoulder: Landmark, wrist: Landmark, visibility_threshold: float = 0.7) -> Optional[float]:
        if all(p.visibility > visibility_threshold for p in [hip, shoulder, wrist]):
            angle = AngleCalculator.angle_deg(hip, shoulder, wrist)
            return min(angle, 360 - angle)
        return None

    @staticmethod
    def calculate_elbow_bend_angle(shoulder: Landmark, elbow: Landmark, wrist: Landmark, visibility_threshold: float = 0.7) -> Optional[float]:
        if all(p.visibility > visibility_threshold for p in [shoulder, elbow, wrist]):
            angle = AngleCalculator.calculate_angle(shoulder, elbow, wrist)
            return min(angle, 360 - angle)
        return None
    
# --- ExerciseCounter class ---
class ExerciseCounter:
    def __init__(self):
        # Shared
        self.total_reps = 0
        self.state_enter_time = None
        self.pending_rep_valid = True
        self.active_arm_side = None

        # Squat - BALANCED ACCURACY (Cân bằng: Chính xác nhưng không quá khó)
        self.squat_counter = 0
        self.squat_state = SquatState.IDLE
        self.squat_feedback_manager = FeedbackManager()
        self.squat_threshold = 95  # IMPROVED: Deeper squat (was 105)
        self.start_threshold = 160  # IMPROVED: Straighter standing (was 145)
        self.squat_start_hip_y = None 
        self.min_hold_time = 0.2
        self.symmetry_threshold = 125
        self.hip_drop_threshold = 0.10  # IMPROVED: Clearer drop (was 0.05)
        self.hip_angle_threshold = 130  # IMPROVED: Better hip fold (was 140)
        self.min_hip_fold = 150
        self.squat_down_hip_y = None

        # Bicep Curl - BALANCED ACCURACY
        self.curl_counter = 0
        self.bicep_curl_state = BicepCurlState.IDLE
        self.bicep_curl_feedback_manager = FeedbackManager()
        self.curl_start_threshold = 162
        self.curl_up_threshold = 60  # IMPROVED: Full curl (was 70)
        self.curl_down_threshold = 162
        self.curl_start_shoulder = None
        self.elbow_position_valid = True
        self.min_concentric_time = 0.5  # NEW: Tempo control (up)
        self.min_eccentric_time = 1.0   # NEW: Tempo control (down)

        # Shoulder Flexion - BALANCED ACCURACY (Independent arm tracking)
        self.shoulder_flexion_counter = 0
        self.shoulder_flexion_state = ShoulderFlexionState.IDLE
        self.shoulder_flexion_feedback_manager = FeedbackManager()
        self.flex_start_threshold = 15
        self.flex_up_threshold = 145  # IMPROVED: Higher reach (was 120)
        self.flex_down_threshold = 30
        self.shoulder_flex_start_shoulder = None
        self.arm_straight_valid = True
        self.recent_elbow_angles = []
        
        # Independent arm state tracking for shoulder flexion
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

        # Knee Raise - Paired tracking (left leg + right arm, right leg + left arm)
        self.knee_raise_counter = 0
        self.knee_raise_state = KneeRaiseState.IDLE
        self.knee_raise_feedback_manager = FeedbackManager()
        self.knee_raise_leg_threshold = 140  # Lenient: raised if <140° (bent nhẹ)
        self.knee_raise_arm_threshold = 80   # Lenient: raised if >80° (giơ ngang)
        self.knee_raise_start_leg_threshold = 150  # Start if leg >150° (straight)
        self.knee_raise_start_arm_threshold = 30   # Start if arm <30° (down)
        self.active_pair_side = None  # 'left_leg_right_arm' or 'right_leg_left_arm'
        self.pair_enter_time = None
        self.pair_valid = True
        self.pair_sync_valid = True
        self.recent_leg_angles = {'left': [], 'right': []}
        self.recent_arm_angles = {'left': [], 'right': []}

        # Thresholds - BALANCED ACCURACY (Cân bằng chính xác và khả thi)
        self.thresholds = {
            # Squat - BALANCED
            'squat_not_deep_enough': 90,
            'squat_too_deep': 60,
            'squat_forward_bend_too_little': 5,   # RELAXED: (was 10)
            'squat_forward_bend_too_much': 60,    # RELAXED: (was 45)
            'squat_knee_forward_max': 0.06,  # BALANCED: Slightly more lenient (was 0.05)
            'squat_knee_valgus_min_ratio': 0.70,  # BALANCED: More lenient (was 0.75)
            # Bicep - BALANCED
            'bicep_curl_not_high_enough': 70,  # BALANCED: Good standard (was 80° too easy, 65° too hard)
            'bicep_curl_not_low_enough': 162,
            'bicep_curl_body_swing': 30,  # RELAXED: Less strict on body swing (was 15)
            'bicep_curl_shoulder_movement': 0.15, # RELAXED: (was 0.08)
            'bicep_curl_elbow_dev_max': 25,  # RELAXED: (was 15)
            # Shoulder Flexion - BALANCED FIX
            'shoulder_flex_not_high_enough': 105,
            'shoulder_flex_elbow_not_straight': 165,
            'shoulder_flex_body_swing': 30, # RELAXED: (was 15)
            'shoulder_flex_shoulder_movement': 0.15, # RELAXED: (was 0.08)
            # Knee Raise - Balanced for elderly
            'knee_raise_leg_not_high_enough': 150,
            'knee_raise_arm_not_high_enough': 60,
            'knee_raise_body_swing': 25, # RELAXED: (was 10)
            'knee_raise_sync_delay_max': 0.8,
            'knee_raise_max_hip_tilt': 0.15,  # RELAXED: (was 0.10)
        }

    def _check_timing(self, duration: float, feedback_manager: FeedbackManager) -> bool:
        """Check if the phase duration is sufficient (min 0.2s for controlled movement)."""
        if duration < 0.05:
            feedback_manager.add_feedback("Quá nhanh", FeedbackPriority.HIGH)
            return False
        return True

    def _check_elbow_position(self, elbow_torso_angle: Optional[float], feedback_manager) -> bool:
        """CRITICAL CHECK: Elbow deviation must be small"""
        if elbow_torso_angle is None:
            return True
        
        deviation = elbow_torso_angle
        if deviation > self.thresholds['bicep_curl_elbow_dev_max']:
            feedback_manager.add_feedback("Khép khuỷu tay lại!", FeedbackPriority.HIGH)
            return False
        
        return True

    def _check_sync_timing(self, leg_time: float, arm_time: float, feedback_manager: FeedbackManager) -> bool:
        """Check if leg and arm movements are synchronized within threshold."""
        if abs(leg_time - arm_time) > self.thresholds['knee_raise_sync_delay_max']:
            feedback_manager.add_feedback("Đồng bộ tay chân", FeedbackPriority.MEDIUM)
            return False
        return True

    def _average_recent_angles(self, angles_list: List[float]) -> Optional[float]:
        """Get average of recent angles for smoothing."""
        if angles_list:
            return sum(angles_list) / len(angles_list)
        return None
        
    def _check_knee_alignment(self, knee: Landmark, ankle: Landmark, 
                             visibility_threshold: float = 0.7) -> Tuple[bool, Optional[str]]:
        """
        NEW: Check if knee goes past toes (knee over toes check)
        Returns: (is_valid, feedback_message)
        """
        if knee.visibility < visibility_threshold or ankle.visibility < visibility_threshold:
            return True, None
        
        # Knee shouldn't go past ankle in x-axis
        knee_forward_distance = knee.x - ankle.x
        
        if knee_forward_distance > self.thresholds['squat_knee_forward_max']:
            return False, "Đầu gối không vượt mũi chân!"
        
        return True, None
    
    def _check_knee_valgus(self, left_knee: Landmark, right_knee: Landmark,
                          left_hip: Landmark, right_hip: Landmark,
                          visibility_threshold: float = 0.7) -> Tuple[bool, Optional[str]]:
        """
        NEW: Check for knee valgus (knees caving in)
        Returns: (is_valid, feedback_message)
        """
        if not all(p.visibility > visibility_threshold for p in [left_knee, right_knee, left_hip, right_hip]):
            return True, None
        
        knee_distance = abs(left_knee.x - right_knee.x)
        hip_distance = abs(left_hip.x - right_hip.x)
        
        # Knee distance should be >= 75% of hip distance
        if knee_distance < hip_distance * self.thresholds['squat_knee_valgus_min_ratio']:
            return False, "Đẩy đầu gối ra ngoài!"
        
        return True, None
    
    def _check_balance(self, left_hip: Landmark, right_hip: Landmark,
                      visibility_threshold: float = 0.7) -> Tuple[bool, Optional[str]]:
        """
        NEW: Check balance during knee raise (hip shouldn't tilt too much)
        Returns: (is_valid, feedback_message)
        """
        if left_hip.visibility < visibility_threshold or right_hip.visibility < visibility_threshold:
            return True, None
        
        hip_tilt = abs(left_hip.y - right_hip.y)
        
        if hip_tilt > self.thresholds['knee_raise_max_hip_tilt']:
            return False, "Giữ thăng bằng!"
        
        return True, None


    def reset_state(self, exercise_name: str):
        if exercise_name == 'squat':
            self.squat_counter = 0
            self.squat_state = SquatState.IDLE
            self.squat_feedback_manager.clear_feedback()
        elif exercise_name == 'bicep-curl':
            self.curl_counter = 0
            self.bicep_curl_state = BicepCurlState.IDLE
            self.bicep_curl_feedback_manager.clear_feedback()
            self.curl_start_shoulder = None
            self.elbow_position_valid = True
        elif exercise_name == 'shoulder-flexion':
            self.shoulder_flexion_counter = 0
            self.shoulder_flexion_state = ShoulderFlexionState.IDLE
            self.shoulder_flexion_feedback_manager.clear_feedback()
            self.shoulder_flex_start_shoulder = None
            self.arm_straight_valid = True
            self.recent_elbow_angles = []
            # Reset independent arm states
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
        elif exercise_name == 'knee-raise':
            self.knee_raise_counter = 0
            self.knee_raise_state = KneeRaiseState.IDLE
            self.knee_raise_feedback_manager.clear_feedback()
            self.active_pair_side = None
            self.pair_enter_time = None
            self.pair_valid = True
            self.pair_sync_valid = True
            self.recent_leg_angles = {'left': [], 'right': []}
            self.recent_arm_angles = {'left': [], 'right': []}
        else:
            # Full reset
            self.squat_counter = 0
            self.squat_state = SquatState.IDLE
            self.squat_feedback_manager.clear_feedback()
            self.curl_counter = 0
            self.bicep_curl_state = BicepCurlState.IDLE
            self.bicep_curl_feedback_manager.clear_feedback()
            self.curl_start_shoulder = None
            self.shoulder_flexion_counter = 0
            self.shoulder_flexion_state = ShoulderFlexionState.IDLE
            self.shoulder_flexion_feedback_manager.clear_feedback()
            self.shoulder_flex_start_shoulder = None
            self.knee_raise_counter = 0
            self.knee_raise_state = KneeRaiseState.IDLE
            self.knee_raise_feedback_manager.clear_feedback()
            self.active_pair_side = None
            self.pair_enter_time = None
            self.pair_valid = True
            self.pair_sync_valid = True
            self.recent_leg_angles = {'left': [], 'right': []}
            self.recent_arm_angles = {'left': [], 'right': []}
            self.total_reps = 0
            self.pending_rep_valid = True
            self.state_enter_time = None
            self.active_arm_side = None
            self.recent_elbow_angles = []
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

    def _process_single_arm_flexion(
        self,
        flexion_angle: Optional[float],
        elbow_angle: Optional[float],
        arm_state: int,
        arm_enter_time: Optional[float],
        arm_valid: bool,
        arm_straight_valid: bool,
        elbow_angles_list: List[float],
        arm_name: str
    ) -> Tuple[int, Optional[float], bool, bool, List[float]]:
        """Process shoulder flexion for a single arm independently"""
        
        if flexion_angle is None:
            return arm_state, arm_enter_time, arm_valid, arm_straight_valid, elbow_angles_list
        
        # Check arm straightness with averaging (less strict)
        if arm_state in [ShoulderFlexionState.FLEXION_START, ShoulderFlexionState.FLEXION_UP, ShoulderFlexionState.FLEXION_DOWN]:
            if elbow_angle is not None:
                elbow_angles_list.append(elbow_angle)
                if len(elbow_angles_list) > 3:
                    elbow_angles_list.pop(0)
                avg_elbow = sum(elbow_angles_list) / len(elbow_angles_list) if elbow_angles_list else elbow_angle
                if avg_elbow is not None and avg_elbow < self.thresholds['shoulder_flex_elbow_not_straight']:
                    self.shoulder_flexion_feedback_manager.add_feedback(f"Thẳng tay {arm_name} ra!", FeedbackPriority.MEDIUM)
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
            self.shoulder_flexion_feedback_manager.start_new_rep()
            
        elif arm_state == ShoulderFlexionState.FLEXION_START and flexion_angle > self.flex_up_threshold:
            if arm_enter_time is not None:
                duration = time.time() - arm_enter_time
                if not self._check_timing(duration, self.shoulder_flexion_feedback_manager):
                    arm_valid = False
            arm_state = ShoulderFlexionState.FLEXION_UP
            arm_enter_time = time.time()
            
        elif arm_state == ShoulderFlexionState.FLEXION_UP and flexion_angle < 70:  # More lenient hysteresis
            arm_state = ShoulderFlexionState.FLEXION_DOWN
            if arm_enter_time is not None:
                duration = time.time() - arm_enter_time
                if not self._check_timing(duration, self.shoulder_flexion_feedback_manager):
                    arm_valid = False
            arm_enter_time = time.time()
            
        elif arm_state == ShoulderFlexionState.FLEXION_DOWN and flexion_angle < self.flex_down_threshold:
            if arm_enter_time is not None:
                duration = time.time() - arm_enter_time
                if not self._check_timing(duration, self.shoulder_flexion_feedback_manager):
                    arm_valid = False
            
            # Count if valid
            if arm_valid and arm_straight_valid:
                self.shoulder_flexion_counter += 1
                self.total_reps += 1
                self.shoulder_flexion_feedback_manager.complete_rep()
            
            # Reset for next rep
            arm_valid = True
            arm_straight_valid = True
            arm_state = ShoulderFlexionState.IDLE
            arm_enter_time = None
            elbow_angles_list = []
        
        return arm_state, arm_enter_time, arm_valid, arm_straight_valid, elbow_angles_list

    def process_shoulder_flexion(
        self,
        left_hip: Landmark, left_shoulder: Landmark, left_elbow: Landmark, left_wrist: Landmark,
        right_hip: Landmark, right_shoulder: Landmark, right_elbow: Landmark, right_wrist: Landmark,
        left_flexion_angle: Optional[float], right_flexion_angle: Optional[float],
        left_elbow_angle: Optional[float], right_elbow_angle: Optional[float],
        hip_shoulder_angle: Optional[float]
    ) -> Tuple[int, List[str]]:
        
        # Process left arm independently
        (self.left_arm_state, self.left_arm_enter_time, self.left_arm_valid, 
         self.left_arm_straight_valid, self.left_elbow_angles) = self._process_single_arm_flexion(
            left_flexion_angle, left_elbow_angle, self.left_arm_state, 
            self.left_arm_enter_time, self.left_arm_valid, self.left_arm_straight_valid,
            self.left_elbow_angles, "left"
        )
        
        # Process right arm independently
        (self.right_arm_state, self.right_arm_enter_time, self.right_arm_valid, 
         self.right_arm_straight_valid, self.right_elbow_angles) = self._process_single_arm_flexion(
            right_flexion_angle, right_elbow_angle, self.right_arm_state, 
            self.right_arm_enter_time, self.right_arm_valid, self.right_arm_straight_valid,
            self.right_elbow_angles, "right"
        )
        
        # Determine which arm is more active for display
        active_state = ShoulderFlexionState.IDLE
        if left_flexion_angle is not None and right_flexion_angle is not None:
            active_state = self.left_arm_state if left_flexion_angle > right_flexion_angle else self.right_arm_state
        elif left_flexion_angle is not None:
            active_state = self.left_arm_state
        elif right_flexion_angle is not None:
            active_state = self.right_arm_state
        
        # Feedback: Range of motion (only if both arms are low)
        if (self.left_arm_state == ShoulderFlexionState.FLEXION_UP or self.right_arm_state == ShoulderFlexionState.FLEXION_UP):
            if left_flexion_angle is not None and left_flexion_angle < self.thresholds['shoulder_flex_not_high_enough']:
                if self.left_arm_state == ShoulderFlexionState.FLEXION_UP:
                    self.shoulder_flexion_feedback_manager.add_feedback("Tay trái cao hơn", FeedbackPriority.LOW)
            if right_flexion_angle is not None and right_flexion_angle < self.thresholds['shoulder_flex_not_high_enough']:
                if self.right_arm_state == ShoulderFlexionState.FLEXION_UP:
                    self.shoulder_flexion_feedback_manager.add_feedback("Tay phải cao hơn", FeedbackPriority.LOW)
        
        # Feedback: Body swing (less priority)
        if hip_shoulder_angle is not None and hip_shoulder_angle > self.thresholds['shoulder_flex_body_swing']:
            self.shoulder_flexion_feedback_manager.add_feedback("Thẳng lưng lên", FeedbackPriority.LOW)
        
        return active_state, self.shoulder_flexion_feedback_manager.get_feedback()

    def process_bicep_curl(
        self, left_shoulder: Landmark, left_elbow: Landmark, left_wrist: Landmark, left_hip: Landmark,
        right_shoulder: Landmark, right_elbow: Landmark, right_wrist: Landmark, right_hip: Landmark,
        left_bicep_angle: Optional[float], right_bicep_angle: Optional[float],
        elbow_torso_result: Tuple[Optional[float], Optional[float], Optional[float], str], 
        hip_shoulder_angle: Optional[float]
    ) -> Tuple[int, List[str]]:
        
        left_elbow_torso = elbow_torso_result[0]
        right_elbow_torso = elbow_torso_result[1]

        # Determine active arm
        active_bicep_angle = None
        active_side = None
        active_elbow_torso = None
        active_wrist = None
        active_elbow = None
        active_shoulder = None
        
        if left_bicep_angle is not None and right_bicep_angle is not None:
            if left_bicep_angle < right_bicep_angle:
                active_bicep_angle = left_bicep_angle
                active_side = 'left'
                active_elbow_torso = left_elbow_torso
                active_wrist = left_wrist
                active_elbow = left_elbow
                active_shoulder = left_shoulder
            else:
                active_bicep_angle = right_bicep_angle
                active_side = 'right'
                active_elbow_torso = right_elbow_torso
                active_wrist = right_wrist
                active_elbow = right_elbow
                active_shoulder = right_shoulder
        elif left_bicep_angle is not None:
            active_bicep_angle = left_bicep_angle
            active_side = 'left'
            active_elbow_torso = left_elbow_torso
            active_wrist = left_wrist
            active_elbow = left_elbow
            active_shoulder = left_shoulder
        elif right_bicep_angle is not None:
            active_bicep_angle = right_bicep_angle
            active_side = 'right'
            active_elbow_torso = right_elbow_torso
            active_wrist = right_wrist
            active_elbow = right_elbow
            active_shoulder = right_shoulder

        if self.active_arm_side != active_side:
            self.active_arm_side = active_side

        if active_bicep_angle is not None:
            # Feedback: Range of motion
            if (self.bicep_curl_state in [BicepCurlState.IDLE, BicepCurlState.CURL_START]) and active_bicep_angle < self.thresholds['bicep_curl_not_low_enough']:
                self.bicep_curl_feedback_manager.add_feedback("Duỗi thẳng tay", FeedbackPriority.MEDIUM)
            
            if self.bicep_curl_state == BicepCurlState.CURL_UP and active_bicep_angle > self.thresholds['bicep_curl_not_high_enough']:
                self.bicep_curl_feedback_manager.add_feedback("Gập cao hơn", FeedbackPriority.MEDIUM)

            # Feedback: Wrist tuck - REMOVED as requested (too strict)
            # if self.bicep_curl_state in [BicepCurlState.CURL_START, BicepCurlState.CURL_UP] and active_wrist and active_elbow:
            #     if not AngleCalculator.check_wrist_tuck(active_elbow, active_wrist):
            #         self.bicep_curl_feedback_manager.add_feedback("Nắm chặt tay, xoay vào trong!", FeedbackPriority.MEDIUM)

            # Critical check: Elbow position
            if self.bicep_curl_state in [BicepCurlState.CURL_START, BicepCurlState.CURL_UP]:
                if not self._check_elbow_position(active_elbow_torso, self.bicep_curl_feedback_manager):
                    self.elbow_position_valid = False

            # State transitions
            if self.bicep_curl_state == BicepCurlState.IDLE and active_bicep_angle > self.curl_start_threshold:
                self.bicep_curl_state = BicepCurlState.CURL_START
                self.state_enter_time = time.time()
                self.elbow_position_valid = True
                self.bicep_curl_feedback_manager.start_new_rep()
                
            elif self.bicep_curl_state == BicepCurlState.CURL_START and active_bicep_angle < self.curl_up_threshold:
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    # Tempo check: Concentric (going up)
                    if duration < self.min_concentric_time:
                        self.bicep_curl_feedback_manager.add_feedback("Lên chậm thôi", FeedbackPriority.HIGH)
                        self.pending_rep_valid = False
                
                self.bicep_curl_state = BicepCurlState.CURL_UP
                self.state_enter_time = time.time()
                if active_shoulder is not None:
                    self.curl_start_shoulder = {'x': active_shoulder.x, 'y': active_shoulder.y}
                else:
                    self.curl_start_shoulder = None
                
            elif self.bicep_curl_state == BicepCurlState.CURL_UP and active_bicep_angle > self.curl_down_threshold:
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    # Tempo check: Eccentric (going down)
                    if duration < self.min_eccentric_time:
                        self.bicep_curl_feedback_manager.add_feedback("Xuống chậm thôi", FeedbackPriority.HIGH)
                        self.pending_rep_valid = False
                
                if self.pending_rep_valid and self.elbow_position_valid:
                    self.curl_counter += 1
                    self.total_reps += 1
                    self.bicep_curl_feedback_manager.complete_rep()
                
                self.pending_rep_valid = True
                self.elbow_position_valid = True
                self.bicep_curl_state = BicepCurlState.CURL_START
                self.curl_start_shoulder = None
                self.state_enter_time = None
                self.bicep_curl_feedback_manager.start_new_rep()

        # Feedback: Body lean/swing
        if hip_shoulder_angle is not None and hip_shoulder_angle > self.thresholds['bicep_curl_body_swing']:
            self.bicep_curl_feedback_manager.add_feedback("Đừng đung đưa người", FeedbackPriority.MEDIUM)
        
        # Feedback: Shoulder movement
        if self.bicep_curl_state == BicepCurlState.CURL_UP and self.curl_start_shoulder is not None and active_shoulder is not None:
            dist = AngleCalculator.find_distance(active_shoulder.x, active_shoulder.y, 
                                                self.curl_start_shoulder['x'], self.curl_start_shoulder['y'])
            if dist > self.thresholds['bicep_curl_shoulder_movement']:
                self.bicep_curl_feedback_manager.add_feedback("Giữ vai cố định", FeedbackPriority.MEDIUM)

        return self.bicep_curl_state, self.bicep_curl_feedback_manager.get_feedback()

    def process_squat(
        self, knee_angle: Optional[float], back_angle: Optional[float], 
        left_hip: Landmark, right_hip: Landmark, left_knee: Landmark, 
        right_knee: Landmark, left_ankle: Landmark, right_ankle: Landmark,
        left_shoulder: Landmark, right_shoulder: Landmark
    ) -> Tuple[int, List[str]]:
        
        # Tính knee riêng (let calculator handle visibility; no redundant None check needed)
        left_knee_angle = AngleCalculator.calculate_knee_angle(left_hip, left_knee, left_ankle, visibility_threshold=0.7)
        right_knee_angle = AngleCalculator.calculate_knee_angle(right_hip, right_knee, right_ankle, visibility_threshold=0.7)
        
        effective_knee_avg = knee_angle
        
        # Tính hip angle riêng (visibility check only)
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
        
        # THÊM DEBUG: Print để check (xóa sau test) - FIXED SYNTAX (format strings outside f-string)
        if effective_knee_avg is not None:
            left_knee_str = f"{left_knee_angle:.1f}" if left_knee_angle is not None else 'None'
            right_knee_str = f"{right_knee_angle:.1f}" if right_knee_angle is not None else 'None'
            print(f"[DEBUG] Knee avg: {effective_knee_avg:.1f}° | Left knee: {left_knee_str}° | Right knee: {right_knee_str}°")
        if hip_angle_avg is not None:
            print(f"[DEBUG] Hip angle avg: {hip_angle_avg:.1f}°")
            if self.squat_start_hip_y is not None:
                print(f"[DEBUG] Hip y drop: {current_hip_y_avg - self.squat_start_hip_y:.3f}")
        
        # Skip nếu NO knee angles available (relaxed: allow one side None, use avg + visible side)
        if effective_knee_avg is None:
            return self.squat_state, self.squat_feedback_manager.get_feedback()
        
        # Use available knee for symmetry (lenient for side view)
        visible_knees = []
        if left_knee_angle is not None:
            visible_knees.append(left_knee_angle)
        if right_knee_angle is not None:
            visible_knees.append(right_knee_angle)
        
        # Skip if no individual knees but avg ok? No, proceed but use avg for symmetry if needed
        if not visible_knees and hip_angle_avg is None:
            return self.squat_state, self.squat_feedback_manager.get_feedback()
        
        # For symmetry, use avg if only one visible, or check diff if both
        effective_symmetry_angle = effective_knee_avg if len(visible_knees) == 1 else None  # For single side
        if len(visible_knees) == 2:
            knee_diff = abs(visible_knees[0] - visible_knees[1])
        else:
            knee_diff = 0  # No diff if single side
        
        print(f"[DEBUG] Current state: {get_state_name(SquatState, self.squat_state)} | Visible knees: {len(visible_knees)} | Knee diff: {knee_diff:.1f}°")
        
        # Feedback: Depth
        if self.squat_state == SquatState.SQUAT_DOWN:
            if effective_knee_avg > self.squat_threshold + 10:
                self.squat_feedback_manager.add_feedback("Xuống sâu hơn", FeedbackPriority.MEDIUM)
            elif effective_knee_avg < 60:
                self.squat_feedback_manager.add_feedback("Quá sâu", FeedbackPriority.MEDIUM)
            
            if hip_angle_avg is not None and hip_angle_avg > self.min_hip_fold:
                self.squat_feedback_manager.add_feedback("Gập hông sâu hơn!", FeedbackPriority.HIGH)
        
        # State transitions (use effective_knee_avg for main logic)
        if self.squat_state == SquatState.IDLE and effective_knee_avg > self.start_threshold:
            self.squat_state = SquatState.SQUAT_START
            self.state_enter_time = time.time()
            self.squat_start_hip_y = current_hip_y_avg
            self.squat_down_hip_y = None  # Reset
            self.pending_rep_valid = True
            self.squat_feedback_manager.start_new_rep()
            print(f"[DEBUG] -> SQUAT_START (knee={effective_knee_avg:.1f}°)")
            
        elif self.squat_state == SquatState.SQUAT_START and effective_knee_avg < self.squat_threshold:
            if self.state_enter_time is not None:
                duration = time.time() - self.state_enter_time
                if not self._check_timing(duration, self.squat_feedback_manager):
                    self.pending_rep_valid = False
            
            # Lenient symmetry: if both visible, check both < threshold or diff <30; if one, check that one
            symmetry_ok = False
            if len(visible_knees) == 2:
                symmetry_ok = (visible_knees[0] < self.symmetry_threshold and visible_knees[1] < self.symmetry_threshold) or knee_diff < 30
            elif len(visible_knees) == 1:
                symmetry_ok = visible_knees[0] < self.squat_threshold  # Use threshold directly for single side
            else:
                symmetry_ok = True  # Fallback if no individuals but avg ok (rare)
            
            if symmetry_ok:
                if hip_angle_avg is not None and hip_angle_avg < self.hip_angle_threshold:
                    self.squat_state = SquatState.SQUAT_DOWN
                    self.state_enter_time = time.time()
                    self.squat_down_hip_y = current_hip_y_avg  # Track hip y at down entry
                    print(f"[DEBUG] -> SQUAT_DOWN (knee={effective_knee_avg:.1f}°)")
                else:
                    if hip_angle_avg is not None:
                        self.squat_feedback_manager.add_feedback("Deeper hip bend!", FeedbackPriority.HIGH)
                    self.pending_rep_valid = False
            else:
                self.squat_feedback_manager.add_feedback("Even squat", FeedbackPriority.MEDIUM)
                self.pending_rep_valid = False
        
        elif self.squat_state == SquatState.SQUAT_DOWN:
            # NEW: Check knee alignment (knee over toes)
            left_knee_valid, left_knee_msg = self._check_knee_alignment(left_knee, left_ankle)
            if not left_knee_valid and left_knee_msg:
                self.squat_feedback_manager.add_feedback(left_knee_msg, FeedbackPriority.HIGH)
                self.pending_rep_valid = False
            
            right_knee_valid, right_knee_msg = self._check_knee_alignment(right_knee, right_ankle)
            if not right_knee_valid and right_knee_msg:
                self.squat_feedback_manager.add_feedback(right_knee_msg, FeedbackPriority.HIGH)
                self.pending_rep_valid = False
            
            # NEW: Check knee valgus (knees caving in)
            valgus_valid, valgus_msg = self._check_knee_valgus(left_knee, right_knee, left_hip, right_hip)
            if not valgus_valid and valgus_msg:
                self.squat_feedback_manager.add_feedback(valgus_msg, FeedbackPriority.HIGH)
                self.pending_rep_valid = False
            

            # Track max hip y during DOWN (deeper drop = higher y)
            if self.squat_down_hip_y is None:
                self.squat_down_hip_y = current_hip_y_avg
            else:
                self.squat_down_hip_y = max(self.squat_down_hip_y, current_hip_y_avg)
            
            if effective_knee_avg > self.start_threshold:
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if duration < self.min_hold_time:
                        self.squat_feedback_manager.add_feedback(f"Hold longer ({self.min_hold_time}s)", FeedbackPriority.LOW)
                        return self.squat_state, self.squat_feedback_manager.get_feedback()
                    
                    # Hip drop check: drop = down_hip_y - start_hip_y > threshold (positive for deeper)
                    actual_drop = self.squat_down_hip_y - self.squat_start_hip_y if self.squat_start_hip_y is not None else 0
                    if actual_drop < self.hip_drop_threshold:
                        self.squat_feedback_manager.add_feedback("Lower hips!", FeedbackPriority.MEDIUM)
                        self.pending_rep_valid = False
                        return self.squat_state, self.squat_feedback_manager.get_feedback()
                    
                    # Final hip angle check
                    if hip_angle_avg is not None and hip_angle_avg > self.hip_angle_threshold:
                        self.squat_feedback_manager.add_feedback("Keep hips bent!", FeedbackPriority.LOW)
                        self.pending_rep_valid = False
                        return self.squat_state, self.squat_feedback_manager.get_feedback()
                    
                    if self.pending_rep_valid:
                        self.squat_counter += 1
                        self.total_reps += 1
                        self.squat_feedback_manager.complete_rep()
                        print(f"[DEBUG] Rep counted! Total squat: {self.squat_counter} (drop={actual_drop:.3f})")
                
                self.pending_rep_valid = True
                self.squat_state = SquatState.SQUAT_START
                self.squat_start_hip_y = current_hip_y_avg  # Update start to current standing
                self.squat_down_hip_y = None
                self.state_enter_time = None
                self.squat_feedback_manager.start_new_rep()
                print(f"[DEBUG] -> SQUAT_START (up from DOWN)")
            else:
                # Still in down, no transition
                pass
        
        # Feedback back angle
        if back_angle is not None and self.squat_state in [SquatState.SQUAT_START, SquatState.SQUAT_DOWN]:
            if back_angle < self.thresholds['squat_forward_bend_too_little']:
                self.squat_feedback_manager.add_feedback("Lean forward", FeedbackPriority.MEDIUM)
            elif back_angle > self.thresholds['squat_forward_bend_too_much']:
                self.squat_feedback_manager.add_feedback("Less lean", FeedbackPriority.MEDIUM)

        return self.squat_state, self.squat_feedback_manager.get_feedback()

    def process_knee_raise(
        self,
        left_hip: Landmark, left_knee: Landmark, left_ankle: Landmark,
        right_hip: Landmark, right_knee: Landmark, right_ankle: Landmark,
        left_shoulder: Landmark, left_wrist: Landmark,
        right_shoulder: Landmark, right_wrist: Landmark,
        left_knee_angle: Optional[float], right_knee_angle: Optional[float],
        left_flexion_angle: Optional[float], right_flexion_angle: Optional[float],
        hip_shoulder_angle: Optional[float]
    ) -> Tuple[int, List[str]]:
        """Process knee raise with opposite arm: left leg + right arm, right leg + left arm. Lenient version."""
        
        # Smooth angles with smaller window (2) for faster detection
        if left_knee_angle is not None:
            self.recent_leg_angles['left'].append(left_knee_angle)
            if len(self.recent_leg_angles['left']) > 2:
                self.recent_leg_angles['left'].pop(0)
            avg_left_knee = self._average_recent_angles(self.recent_leg_angles['left']) or left_knee_angle
        else:
            avg_left_knee = None

        if right_knee_angle is not None:
            self.recent_leg_angles['right'].append(right_knee_angle)
            if len(self.recent_leg_angles['right']) > 2:
                self.recent_leg_angles['right'].pop(0)
            avg_right_knee = self._average_recent_angles(self.recent_leg_angles['right']) or right_knee_angle
        else:
            avg_right_knee = None

        if left_flexion_angle is not None:
            self.recent_arm_angles['left'].append(left_flexion_angle)
            if len(self.recent_arm_angles['left']) > 2:
                self.recent_arm_angles['left'].pop(0)
            avg_left_flex = self._average_recent_angles(self.recent_arm_angles['left']) or left_flexion_angle
        else:
            avg_left_flex = None

        if right_flexion_angle is not None:
            self.recent_arm_angles['right'].append(right_flexion_angle)
            if len(self.recent_arm_angles['right']) > 2:
                self.recent_arm_angles['right'].pop(0)
            avg_right_flex = self._average_recent_angles(self.recent_arm_angles['right']) or right_flexion_angle
        else:
            avg_right_flex = None

        # Determine active pair based on which leg is more bent (lower angle = more bent)
        active_pair = None
        if avg_left_knee is not None and avg_right_knee is not None:
            active_pair = 'left_leg_right_arm' if avg_left_knee < avg_right_knee else 'right_leg_left_arm'
        elif avg_left_knee is not None:
            active_pair = 'left_leg_right_arm'
        elif avg_right_knee is not None:
            active_pair = 'right_leg_left_arm'

        if self.active_pair_side != active_pair:
            self.active_pair_side = active_pair

        if active_pair and avg_left_knee is not None and avg_right_knee is not None and avg_left_flex is not None and avg_right_flex is not None:
            # Get relevant angles for the active pair
            if active_pair == 'left_leg_right_arm':
                leg_angle = avg_left_knee
                arm_angle = avg_right_flex
            else:
                leg_angle = avg_right_knee
                arm_angle = avg_left_flex

            current_time = time.time()
            
            # NEW: Check balance (hip tilt)
            balance_valid, balance_msg = self._check_balance(left_hip, right_hip)
            if not balance_valid and balance_msg:
                self.knee_raise_feedback_manager.add_feedback(balance_msg, FeedbackPriority.HIGH)
                self.pair_valid = False


            # Feedback: Range only when transitioning, not in idle
            if self.knee_raise_state == KneeRaiseState.RAISE_START or self.knee_raise_state == KneeRaiseState.RAISE_UP:
                # Only give feedback if significantly off target
                if leg_angle > 160:  # Leg barely bent
                    self.knee_raise_feedback_manager.add_feedback("Knee higher", FeedbackPriority.MEDIUM)
                if arm_angle < 50:  # Arm barely raised
                    self.knee_raise_feedback_manager.add_feedback("Arm higher", FeedbackPriority.MEDIUM)

            # Body swing - less strict
            if hip_shoulder_angle is not None and hip_shoulder_angle > self.thresholds['knee_raise_body_swing']:
                self.knee_raise_feedback_manager.add_feedback("Balance", FeedbackPriority.LOW)

            # State transitions - FIXED LOGIC
            if self.knee_raise_state == KneeRaiseState.IDLE:
                # Start when BOTH leg straightens AND arm is down
                leg_straight = leg_angle > self.knee_raise_start_leg_threshold  # >150° = straight
                arm_down = arm_angle < self.knee_raise_start_arm_threshold  # <30° = down
                
                if leg_straight and arm_down:
                    self.knee_raise_state = KneeRaiseState.RAISE_START
                    self.pair_enter_time = current_time
                    self.pair_valid = True
                    self.pair_sync_valid = True
                    self.knee_raise_feedback_manager.start_new_rep()
                
            elif self.knee_raise_state == KneeRaiseState.RAISE_START:
                # Move to UP when BOTH leg bends AND arm raises
                leg_raised = leg_angle < self.knee_raise_leg_threshold  # <140° = bent/raised
                arm_raised = arm_angle > self.knee_raise_arm_threshold  # >80° = raised high
                
                if leg_raised and arm_raised:
                    if self.pair_enter_time is not None:
                        duration = current_time - self.pair_enter_time
                        if self._check_timing(duration, self.knee_raise_feedback_manager):
                            self.knee_raise_state = KneeRaiseState.RAISE_UP
                            self.pair_enter_time = current_time
                        else:
                            self.pair_valid = False
                    else:
                        self.knee_raise_state = KneeRaiseState.RAISE_UP
                        self.pair_enter_time = current_time
                elif leg_raised and not arm_raised:
                    # Leg is up but arm is not
                    self.knee_raise_feedback_manager.add_feedback("Arm now", FeedbackPriority.HIGH)
                elif arm_raised and not leg_raised:
                    # Arm is up but leg is not
                    self.knee_raise_feedback_manager.add_feedback("Knee now", FeedbackPriority.HIGH)

            elif self.knee_raise_state == KneeRaiseState.RAISE_UP:
                # Complete rep when BOTH return to start position
                leg_lowered = leg_angle > self.knee_raise_start_leg_threshold  # >150° = straight again
                arm_lowered = arm_angle < self.knee_raise_start_arm_threshold  # <30° = down again
                
                if leg_lowered and arm_lowered:
                    # Count the rep
                    if self.pair_valid and self.pair_sync_valid:
                        self.knee_raise_counter += 1
                        self.total_reps += 1
                        self.knee_raise_feedback_manager.complete_rep()
                    
                    # Reset for next rep
                    self.pair_valid = True
                    self.pair_sync_valid = True
                    self.knee_raise_state = KneeRaiseState.IDLE
                    self.pair_enter_time = None

        return self.knee_raise_state, self.knee_raise_feedback_manager.get_feedback()


# Global instance to maintain state across HTTP requests
EXERCISE_COUNTER = ExerciseCounter()
prev_reps = {}

def calculate_all_angles(landmarks: List[Landmark]) -> Dict[str, Any]:
    """Calculate all relevant angles from landmarks"""
    if len(landmarks) < 33:
        return {'error': 'Insufficient landmarks'}

    left_shoulder = landmarks[11]; right_shoulder = landmarks[12]
    left_elbow = landmarks[13]; right_elbow = landmarks[14]
    left_wrist = landmarks[15]; right_wrist = landmarks[16]
    left_hip = landmarks[23]; right_hip = landmarks[24]
    left_knee = landmarks[25]; right_knee = landmarks[26]
    left_ankle = landmarks[27]; right_ankle = landmarks[28]

    left_bicep_angle = AngleCalculator.calculate_bicep_angle(left_shoulder, left_elbow, left_wrist, 0.7)
    right_bicep_angle = AngleCalculator.calculate_bicep_angle(right_shoulder, right_elbow, right_wrist, 0.7)
    elbow_torso_result = AngleCalculator.calculate_elbow_torso_angle(left_hip, left_shoulder, left_elbow, right_hip, right_shoulder, right_elbow, 0.7)
    hip_shoulder_angle = AngleCalculator.calculate_hip_shoulder_angle(left_hip, left_shoulder, 0.7)
    knee_angle_avg = AngleCalculator.calculate_average_knee_angle(left_hip, left_knee, left_ankle, right_hip, right_knee, right_ankle, 0.7)
    left_knee_angle = AngleCalculator.calculate_knee_angle(left_hip, left_knee, left_ankle, 0.7)
    right_knee_angle = AngleCalculator.calculate_knee_angle(right_hip, right_knee, right_ankle, 0.7)

    left_back_angle = AngleCalculator.calculate_hip_shoulder_angle(left_hip, left_shoulder, 0.7)
    right_back_angle = AngleCalculator.calculate_hip_shoulder_angle(right_hip, right_shoulder, 0.7)
    back_angle = (left_back_angle + right_back_angle) / 2 if left_back_angle and right_back_angle else (left_back_angle or right_back_angle)

    # Shoulder Flexion angles
    left_flexion_angle = AngleCalculator.calculate_shoulder_flexion_angle(left_hip, left_shoulder, left_wrist, 0.7)
    right_flexion_angle = AngleCalculator.calculate_shoulder_flexion_angle(right_hip, right_shoulder, right_wrist, 0.7)
    left_elbow_angle = AngleCalculator.calculate_elbow_bend_angle(left_shoulder, left_elbow, left_wrist, 0.7)
    right_elbow_angle = AngleCalculator.calculate_elbow_bend_angle(right_shoulder, right_elbow, right_wrist, 0.7)

    return {
        'landmarks': landmarks,
        'left_bicep_angle': left_bicep_angle,
        'right_bicep_angle': right_bicep_angle,
        'elbow_torso_result': elbow_torso_result,
        'hip_shoulder_angle': hip_shoulder_angle,
        'knee_angle_avg': knee_angle_avg,
        'left_knee_angle': left_knee_angle,
        'right_knee_angle': right_knee_angle,
        'back_angle': back_angle,
        'left_flexion_angle': left_flexion_angle,
        'right_flexion_angle': right_flexion_angle,
        'left_elbow_angle': left_elbow_angle,
        'right_elbow_angle': right_elbow_angle
    }