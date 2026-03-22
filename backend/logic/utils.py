import math
from typing import List
from .common import Landmark, FeedbackPriority

def get_state_name(state_class, state_value):
    state_dict = {v: k for k, v in state_class.__dict__.items() if isinstance(v, int)}
    return state_dict.get(state_value, "UNKNOWN")

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
        return self.rep_summary if self.rep_completed else self.current_feedback

    def clear_feedback(self):
        self.feedback_window = []
        self.current_feedback = []
        self.priority_queue = []
        self.rep_completed = False
        self.rep_summary = []

class AngleCalculator:
    RAD_TO_DEG = 180.0 / math.pi
    
    @staticmethod
    def calculate_angle(a: Landmark, b: Landmark, c: Landmark) -> float:
        radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
        angle = abs(radians * AngleCalculator.RAD_TO_DEG)
        return angle if angle <= 180 else 360 - angle

    @staticmethod
    def calculate_vertical_angle(point1: List[float], point2: List[float]) -> float:
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return abs(math.atan2(dx, -dy) * AngleCalculator.RAD_TO_DEG)

    @staticmethod
    def find_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        dx = x2 - x1; dy = y2 - y1
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def angle_deg(p1, pref, p2) -> float:
        def get_coords(p):
            if isinstance(p, Landmark): return [p.x, p.y]
            elif isinstance(p, (list, tuple)): return p[:2]
            return [0, 0]
        p1c = get_coords(p1); prc = get_coords(pref); p2c = get_coords(p2)
        p1ref = [p1c[0] - prc[0], p1c[1] - prc[1]]
        p2ref = [p2c[0] - prc[0], p2c[1] - prc[1]]
        dot = p1ref[0] * p2ref[0] + p1ref[1] * p2ref[1]
        mag1 = math.sqrt(p1ref[0]**2 + p1ref[1]**2)
        mag2 = math.sqrt(p2ref[0]**2 + p2ref[1]**2)
        if mag1 == 0 or mag2 == 0: return 0.0
        cos_theta = max(-1, min(1, dot / (mag1 * mag2)))
        return math.acos(cos_theta) * 180 / math.pi

    @staticmethod
    def calculate_elbow_torso_angle(lh, ls, le, rh, rs, re, vt=0.6):
        def is_visible(pts): return all(p.visibility > vt for p in pts)
        lv = is_visible([lh, ls, le]); rv = is_visible([rh, rs, re])
        la = AngleCalculator.angle_deg(lh, ls, le) if lv else None
        ra = AngleCalculator.angle_deg(rh, rs, re) if rv else None
        if lv and rv: return la, ra, (la + ra) / 2, "front"
        elif lv: return la, None, la, "left_side"
        elif rv: return None, ra, ra, "right_side"
        return None, None, None, "unclear"

    @staticmethod
    def calculate_hip_shoulder_angle(hip, shoulder, vt=0.6):
        if hip.visibility > vt and shoulder.visibility > vt:
            return AngleCalculator.calculate_vertical_angle([hip.x, hip.y], [shoulder.x, shoulder.y])
        return None

    @staticmethod
    def calculate_knee_angle(hip, knee, ankle, vt=0.6):
        if all(p.visibility > vt for p in [hip, knee, ankle]):
            return AngleCalculator.calculate_angle(hip, knee, ankle)
        return None

    @staticmethod
    def calculate_average_knee_angle(lh, lk, la, rh, rk, ra, vt=0.6):
        lak = AngleCalculator.calculate_knee_angle(lh, lk, la, vt)
        rak = AngleCalculator.calculate_knee_angle(rh, rk, ra, vt)
        if lak is not None and rak is not None: return (lak + rak) / 2
        return lak if lak is not None else rak

    @staticmethod
    def calculate_bicep_angle(s, e, w, vt=0.6):
        if all(p.visibility > vt for p in [s, e, w]):
            return AngleCalculator.calculate_angle(s, e, w)
        return None

    @staticmethod
    def calculate_shoulder_flexion_angle(h, s, w, vt=0.7):
        if all(p.visibility > vt for p in [h, s, w]):
            a = AngleCalculator.angle_deg(h, s, w)
            return min(a, 360 - a)
        return None

    @staticmethod
    def calculate_elbow_bend_angle(s, e, w, vt=0.7):
        if all(p.visibility > vt for p in [s, e, w]):
            a = AngleCalculator.calculate_angle(s, e, w)
            return min(a, 360 - a)
        return None
