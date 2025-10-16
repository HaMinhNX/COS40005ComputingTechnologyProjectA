# V2/medic1/backend/exercise_logic.py

import math
import time
from typing import List, Dict, Optional, Tuple

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
        high_pri = [self.priority_queue[0]['feedback']] if self.priority_queue else []
        frequent = list(self.current_feedback)
        
        all_feedback = list(set(high_pri + frequent))
        
        def sort_key(feedback):
            max_pri = FeedbackPriority.LOW
            for item in self.priority_queue:
                if item['feedback'] == feedback:
                    max_pri = max(max_pri, -item['priority'])  # FIXED: Use -priority for descending
            return max_pri

        all_feedback.sort(key=sort_key, reverse=True)
        
        return all_feedback[:2]

    def clear_feedback(self):
        self.feedback_window = []
        self.current_feedback = []
        self.priority_queue = []

# --- AngleCalculator class ---
class AngleCalculator:
    @staticmethod
    def calculate_angle(a: Landmark, b: Landmark, c: Landmark) -> float:
        a_coords = [a.x, a.y]
        b_coords = [b.x, b.y]
        c_coords = [c.x, c.y]
        
        radians = math.atan2(c_coords[1] - b_coords[1], c_coords[0] - b_coords[0]) - \
                  math.atan2(a_coords[1] - b_coords[1], a_coords[0] - b_coords[0])
        
        angle = abs(radians * 180.0 / math.pi)
        return angle if angle <= 180 else 360 - angle

    @staticmethod
    def calculate_vertical_angle(point1: List[float], point2: List[float]) -> float:
        x1, y1 = point1
        x2, y2 = point2
        dx = x2 - x1
        dy = y2 - y1
        return abs(math.atan2(dx, -dy) * 180.0 / math.pi)

    @staticmethod
    def find_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

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
                avg_angle = 0.0  # Fallback (không xảy ra do visibility)
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

class ExerciseCounter:
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.curl_counter = 0
        self.bicep_curl_state = BicepCurlState.IDLE
        self.curl_start_threshold = 160
        self.curl_up_threshold = 60
        self.curl_down_threshold = 140
        self.curl_start_shoulder = None
        self.active_arm_side = None

        self.squat_counter = 0
        self.squat_state = SquatState.IDLE
        self.squat_threshold = 90
        self.start_threshold = 160

        self.thresholds = thresholds if thresholds is not None else {
            'squat_too_deep': 70,
            'squat_not_deep_enough': 100,
            'squat_forward_bend_too_little': 10,
            'squat_forward_bend_too_much': 30,
            'bicep_curl_not_low_enough': 170,
            'bicep_curl_not_high_enough': 70,
            'bicep_curl_elbow_dev_max': 35,  # Max deviation allowed (nới lỏng từ 15° ngầm, cho tucked ~20-30° OK)
            'bicep_curl_body_swing': 15,  # Nới lỏng từ 10
            'bicep_curl_shoulder_movement': 0.08,  # Nới lỏng từ 0.05
            'bicep_curl_wrist_tuck_threshold': 0.05
        }

        self.timing_thresholds = {
            'min_phase_time': 0.35,
            'max_phase_time': 3.5  
        }

        self.total_reps = 0
        self.bicep_curl_feedback_manager = FeedbackManager()
        self.squat_feedback_manager = FeedbackManager()

        self.state_enter_time = None
        self.pending_rep_valid = True
        self.elbow_position_valid = True 

    def reset_state(self, exercise_name: str):
        self.total_reps = 0
        if exercise_name == 'squat':
            self.squat_counter = 0
            self.squat_state = SquatState.IDLE
            self.squat_feedback_manager.clear_feedback()
        elif exercise_name == 'bicep-curl':
            self.curl_counter = 0
            self.bicep_curl_state = BicepCurlState.IDLE
            self.curl_start_shoulder = None
            self.active_arm_side = None
            self.bicep_curl_feedback_manager.clear_feedback()
        else:
            self.squat_counter = 0
            self.squat_state = SquatState.IDLE
            self.curl_counter = 0
            self.bicep_curl_state = BicepCurlState.IDLE
            self.curl_start_shoulder = None
            self.active_arm_side = None
            self.squat_feedback_manager.clear_feedback()
            self.bicep_curl_feedback_manager.clear_feedback()

        self.state_enter_time = None
        self.pending_rep_valid = True
        self.elbow_position_valid = True

    def _check_timing(self, duration: float, feedback_manager) -> bool:
        """Check timing - ONLY block rep if too fast or too slow (critical error)"""
        min_time = self.timing_thresholds['min_phase_time']
        max_time = self.timing_thresholds['max_phase_time']
        if duration < min_time:
            feedback_manager.add_feedback("QUÁ NHANH - GIẢM TỐC XUỐNG!", FeedbackPriority.HIGH)
            return False  # Block rep
        elif duration > max_time:
            feedback_manager.add_feedback("QUÁ CHẬM - TĂNG TỐC LÊN!", FeedbackPriority.HIGH)
            return False  # Block rep
        return True  # Allow rep

    def _check_elbow_position(self, elbow_torso_angle: Optional[float], feedback_manager) -> bool:
        """CRITICAL CHECK: Elbow deviation must be small (góc lệch <35° for tucked)"""
        if elbow_torso_angle is None:
            print(f"DEBUG: Elbow angle None - allowing")  # Debug: Comment out after test
            return True  # If can't measure, allow it
        
        #Check if deviation (góc lệch) > max allowed (small angle = good tuck)
        deviation = elbow_torso_angle  # Raw angle is deviation from 0° (collinear)
        if deviation > self.thresholds['bicep_curl_elbow_dev_max']:
            print(f"DEBUG: Elbow deviation {deviation:.1f}° > {self.thresholds['bicep_curl_elbow_dev_max']}° - invalid")  # Debug
            feedback_manager.add_feedback("KHUỶU TAY PHẢI SÁT THÂN NGƯỜI!", FeedbackPriority.HIGH)
            return False  # Block rep - elbow flared/raised too much
        
        print(f"DEBUG: Elbow deviation {deviation:.1f}° OK")  # Debug: Good frame
        return True  # Elbow position is good

    def process_bicep_curl(
        self, left_shoulder: Landmark, left_elbow: Landmark, left_wrist: Landmark, left_hip: Landmark,
        right_shoulder: Landmark, right_elbow: Landmark, right_wrist: Landmark, right_hip: Landmark,
        left_bicep_angle: Optional[float], right_bicep_angle: Optional[float],
        elbow_torso_result: Tuple[Optional[float], Optional[float], Optional[float], str], 
        hip_shoulder_angle: Optional[float]
    ) -> Tuple[int, List[str]]:
        
        left_elbow_torso = elbow_torso_result[0]
        right_elbow_torso = elbow_torso_result[1]

        # Determine active arm (smaller angle = more bent = active)
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
            # FEEDBACK ONLY (doesn't block counting) - Range of motion
            if (self.bicep_curl_state in [BicepCurlState.IDLE, BicepCurlState.CURL_START]) and active_bicep_angle < self.thresholds['bicep_curl_not_low_enough']:
                self.bicep_curl_feedback_manager.add_feedback("Duỗi tay thẳng hoàn toàn ở dưới", FeedbackPriority.MEDIUM)
            
            if self.bicep_curl_state == BicepCurlState.CURL_UP and active_bicep_angle > self.thresholds['bicep_curl_not_high_enough']:
                self.bicep_curl_feedback_manager.add_feedback("Gập tay cao hơn nữa", FeedbackPriority.MEDIUM)

            # FEEDBACK ONLY - Wrist tuck (fist position)
            if self.bicep_curl_state in [BicepCurlState.CURL_START, BicepCurlState.CURL_UP] and active_wrist and active_elbow:
                if not AngleCalculator.check_wrist_tuck(active_elbow, active_wrist):
                    self.bicep_curl_feedback_manager.add_feedback("Gập nắm tay chặt và úp lòng bàn tay vào người!", FeedbackPriority.MEDIUM)

            # CRITICAL CHECK - Elbow position (continuously check during active states)
            if self.bicep_curl_state in [BicepCurlState.CURL_START, BicepCurlState.CURL_UP]:
                if not self._check_elbow_position(active_elbow_torso, self.bicep_curl_feedback_manager):
                    self.elbow_position_valid = False  # Mark as invalid if elbow flares

            # State transitions with TIMING CHECK ONLY (critical error)
            if self.bicep_curl_state == BicepCurlState.IDLE and active_bicep_angle > self.curl_start_threshold:
                self.bicep_curl_state = BicepCurlState.CURL_START
                self.state_enter_time = time.time()
                self.elbow_position_valid = True  # Reset elbow validity at start of rep
                
            elif self.bicep_curl_state == BicepCurlState.CURL_START and active_bicep_angle < self.curl_up_threshold:
                # Up phase complete - check timing ONLY
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if not self._check_timing(duration, self.bicep_curl_feedback_manager):
                        self.pending_rep_valid = False
                
                self.bicep_curl_state = BicepCurlState.CURL_UP
                self.state_enter_time = time.time()
                self.curl_start_shoulder = {'x': active_shoulder.x, 'y': active_shoulder.y}
                
            elif self.bicep_curl_state == BicepCurlState.CURL_UP and active_bicep_angle > self.curl_down_threshold:
                # Down phase complete - check timing ONLY
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if not self._check_timing(duration, self.bicep_curl_feedback_manager):
                        self.pending_rep_valid = False
                
                # COUNT only if timing AND elbow position were valid throughout
                if self.pending_rep_valid and self.elbow_position_valid:
                    self.curl_counter += 1
                    self.total_reps += 1
                
                # Reset for next rep
                self.pending_rep_valid = True
                self.elbow_position_valid = True
                self.bicep_curl_state = BicepCurlState.CURL_START
                self.curl_start_shoulder = None
                self.state_enter_time = None

        # FEEDBACK ONLY - Body lean/swing
        if hip_shoulder_angle is not None and hip_shoulder_angle > self.thresholds['bicep_curl_body_swing']:
            self.bicep_curl_feedback_manager.add_feedback("Giữ người thẳng, không lắc", FeedbackPriority.MEDIUM)
        
        # FEEDBACK ONLY - Shoulder movement
        if self.bicep_curl_state == BicepCurlState.CURL_UP and self.curl_start_shoulder and active_shoulder:
            dist = AngleCalculator.find_distance(active_shoulder.x, active_shoulder.y, 
                                                self.curl_start_shoulder['x'], self.curl_start_shoulder['y'])
            if dist > self.thresholds['bicep_curl_shoulder_movement']:
                self.bicep_curl_feedback_manager.add_feedback("Giữ vai ổn định, không vung", FeedbackPriority.MEDIUM)

        return self.bicep_curl_state, self.bicep_curl_feedback_manager.get_feedback()

    def process_squat(
        self, knee_angle: Optional[float], back_angle: Optional[float], 
        left_hip: Optional[Landmark], right_hip: Optional[Landmark], left_knee: Optional[Landmark], 
        right_knee: Optional[Landmark], left_ankle: Optional[Landmark], right_ankle: Optional[Landmark]
    ) -> Tuple[int, List[str]]:
        
        effective_knee_angle = knee_angle

        if effective_knee_angle is not None:
            # FEEDBACK ONLY (during active squat) - Depth
            if self.squat_state == SquatState.SQUAT_DOWN:
                if effective_knee_angle > self.thresholds['squat_not_deep_enough']:
                    self.squat_feedback_manager.add_feedback("Hạ người xuống sâu hơn", FeedbackPriority.MEDIUM)
                elif effective_knee_angle < self.thresholds['squat_too_deep']:
                    self.squat_feedback_manager.add_feedback("Không nên xuống quá sâu", FeedbackPriority.MEDIUM)
            
            # State transitions with TIMING CHECK ONLY
            if self.squat_state == SquatState.IDLE and effective_knee_angle > self.start_threshold:
                self.squat_state = SquatState.SQUAT_START
                self.state_enter_time = time.time()
                
            elif self.squat_state == SquatState.SQUAT_START and effective_knee_angle < self.squat_threshold:
                # Down phase complete
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if not self._check_timing(duration, self.squat_feedback_manager):
                        self.pending_rep_valid = False
                
                self.squat_state = SquatState.SQUAT_DOWN
                self.state_enter_time = time.time()
                
            elif self.squat_state == SquatState.SQUAT_DOWN and effective_knee_angle > self.start_threshold:
                # Up phase complete
                if self.state_enter_time is not None:
                    duration = time.time() - self.state_enter_time
                    if not self._check_timing(duration, self.squat_feedback_manager):
                        self.pending_rep_valid = False
                
                # COUNT if timing was valid
                if self.pending_rep_valid:
                    self.squat_counter += 1
                    self.total_reps += 1
                
                # Reset for next rep
                self.pending_rep_valid = True
                self.squat_state = SquatState.SQUAT_START
                self.state_enter_time = None

        # FEEDBACK ONLY (during active squat) - Forward bend
        # Only show during ACTIVE squat states, not IDLE
        if back_angle is not None and self.squat_state in [SquatState.SQUAT_START, SquatState.SQUAT_DOWN]:
            if back_angle < self.thresholds['squat_forward_bend_too_little']:
                self.squat_feedback_manager.add_feedback("Nghiêng người về trước hơn", FeedbackPriority.MEDIUM)
            elif back_angle > self.thresholds['squat_forward_bend_too_much']:
                self.squat_feedback_manager.add_feedback("Đừng nghiêng quá xa về trước", FeedbackPriority.MEDIUM)

        return self.squat_state, self.squat_feedback_manager.get_feedback()


# Global instance to maintain state across HTTP requests
EXERCISE_COUNTER = ExerciseCounter()