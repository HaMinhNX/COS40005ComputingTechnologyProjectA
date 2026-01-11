# KẾ HOẠCH CẢI THIỆN LOGIC TẬP LUYỆN

## MỤC TIÊU
Cải thiện độ chính xác và hiệu quả của 4 bài tập thể dục mà KHÔNG phá vỡ logic hiện tại.

## NGUYÊN TẮC
1. ✅ Giữ nguyên cấu trúc state machine
2. ✅ Giữ nguyên API interface
3. ✅ Backward compatible
4. ✅ Incremental improvements
5. ✅ Test thoroughly trước khi deploy

---

## CẢI THIỆN 1: SQUAT (Độ ưu tiên: CRITICAL)

### Vấn đề hiện tại:
```python
# Quá lỏng lẻo
squat_threshold = 110°      # Cho phép squat nông
start_threshold = 135°      # Đứng không thẳng
hip_angle_threshold = 150°  # Gập hông không đủ
hip_drop_threshold = 0.03   # Drop quá nhỏ
```

### Giải pháp đề xuất:

#### Bước 1: Tạo difficulty levels
```python
class SquatDifficulty:
    EASY = {
        'squat_threshold': 110,
        'start_threshold': 145,
        'hip_angle_threshold': 145,
        'hip_drop_threshold': 0.05,
        'symmetry_threshold': 135
    }
    
    NORMAL = {
        'squat_threshold': 95,
        'start_threshold': 160,
        'hip_angle_threshold': 130,
        'hip_drop_threshold': 0.08,
        'symmetry_threshold': 120
    }
    
    HARD = {
        'squat_threshold': 85,
        'start_threshold': 170,
        'hip_angle_threshold': 120,
        'hip_drop_threshold': 0.12,
        'symmetry_threshold': 110
    }
```

#### Bước 2: Thêm knee alignment check
```python
def check_knee_alignment(self, knee: Landmark, ankle: Landmark, 
                        hip: Landmark, visibility_threshold: float = 0.7) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra đầu gối có vượt qua mũi chân không (knee over toes)
    Returns: (is_valid, feedback_message)
    """
    if knee.visibility < visibility_threshold or ankle.visibility < visibility_threshold:
        return True, None
    
    # Knee không nên vượt quá ankle theo trục x
    knee_forward_distance = knee.x - ankle.x
    
    # Cho phép một chút tolerance (5% screen width)
    if knee_forward_distance > 0.05:
        return False, "Đầu gối không vượt mũi chân!"
    
    return True, None

def check_knee_valgus(self, left_knee: Landmark, right_knee: Landmark,
                     left_hip: Landmark, right_hip: Landmark,
                     visibility_threshold: float = 0.7) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra đầu gối có xẹp vào trong không (knee valgus)
    Returns: (is_valid, feedback_message)
    """
    if not all(p.visibility > visibility_threshold for p in [left_knee, right_knee, left_hip, right_hip]):
        return True, None
    
    knee_distance = abs(left_knee.x - right_knee.x)
    hip_distance = abs(left_hip.x - right_hip.x)
    
    # Khoảng cách đầu gối nên >= 80% khoảng cách hông
    if knee_distance < hip_distance * 0.75:
        return False, "Đẩy đầu gối ra ngoài!"
    
    return True, None
```

#### Bước 3: Cải thiện process_squat
```python
def process_squat(
    self, knee_angle: Optional[float], back_angle: Optional[float], 
    left_hip: Landmark, right_hip: Landmark, left_knee: Landmark, 
    right_knee: Landmark, left_ankle: Landmark, right_ankle: Landmark,
    left_shoulder: Landmark, right_shoulder: Landmark,
    difficulty: str = 'NORMAL'  # NEW PARAMETER
) -> Tuple[int, List[str]]:
    
    # Load difficulty settings
    diff_settings = getattr(SquatDifficulty, difficulty.upper(), SquatDifficulty.NORMAL)
    
    # ... existing code ...
    
    # NEW: Check knee alignment during DOWN state
    if self.squat_state == SquatState.SQUAT_DOWN:
        # Check left knee
        left_valid, left_msg = self.check_knee_alignment(left_knee, left_ankle, left_hip)
        if not left_valid and left_msg:
            self.squat_feedback_manager.add_feedback(left_msg, FeedbackPriority.HIGH)
            self.pending_rep_valid = False
        
        # Check right knee
        right_valid, right_msg = self.check_knee_alignment(right_knee, right_ankle, right_hip)
        if not right_valid and right_msg:
            self.squat_feedback_manager.add_feedback(right_msg, FeedbackPriority.HIGH)
            self.pending_rep_valid = False
        
        # Check knee valgus
        valgus_valid, valgus_msg = self.check_knee_valgus(left_knee, right_knee, left_hip, right_hip)
        if not valgus_valid and valgus_msg:
            self.squat_feedback_manager.add_feedback(valgus_msg, FeedbackPriority.HIGH)
            self.pending_rep_valid = False
    
    # Use difficulty settings for thresholds
    if self.squat_state == SquatState.SQUAT_START and effective_knee_avg < diff_settings['squat_threshold']:
        # ... transition to DOWN ...
    
    # ... rest of existing code ...
```

---

## CẢI THIỆN 2: BICEP CURL (Độ ưu tiên: HIGH)

### Vấn đề hiện tại:
```python
curl_up_threshold = 80°         # Không đủ cao
elbow_dev_max = 20°             # Hơi lỏng
# Thiếu tempo control
```

### Giải pháp đề xuất:

#### Bước 1: Tăng độ khó ROM
```python
class BicepCurlDifficulty:
    EASY = {
        'curl_start_threshold': 155,
        'curl_up_threshold': 90,
        'curl_down_threshold': 155,
        'elbow_dev_max': 25,
        'min_concentric_time': 0.3,
        'min_eccentric_time': 0.5
    }
    
    NORMAL = {
        'curl_start_threshold': 165,
        'curl_up_threshold': 60,
        'curl_down_threshold': 165,
        'elbow_dev_max': 18,
        'min_concentric_time': 0.5,
        'min_eccentric_time': 1.0
    }
    
    HARD = {
        'curl_start_threshold': 175,
        'curl_up_threshold': 45,
        'curl_down_threshold': 175,
        'elbow_dev_max': 12,
        'min_concentric_time': 0.8,
        'min_eccentric_time': 1.5
    }
```

#### Bước 2: Thêm tempo control
```python
def check_curl_tempo(self, phase_duration: float, phase_type: str, 
                    difficulty: str = 'NORMAL') -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra tempo của bicep curl
    phase_type: 'concentric' (gập lên) hoặc 'eccentric' (duỗi xuống)
    """
    diff_settings = getattr(BicepCurlDifficulty, difficulty.upper(), BicepCurlDifficulty.NORMAL)
    
    if phase_type == 'concentric':
        min_time = diff_settings['min_concentric_time']
        if phase_duration < min_time:
            return False, f"Gập chậm lại ({min_time}s)!"
    
    elif phase_type == 'eccentric':
        min_time = diff_settings['min_eccentric_time']
        if phase_duration < min_time:
            return False, f"Duỗi chậm lại ({min_time}s)!"
    
    return True, None
```

#### Bước 3: Cải thiện process_bicep_curl
```python
def process_bicep_curl(
    self, left_shoulder: Landmark, left_elbow: Landmark, left_wrist: Landmark, left_hip: Landmark,
    right_shoulder: Landmark, right_elbow: Landmark, right_wrist: Landmark, right_hip: Landmark,
    left_bicep_angle: Optional[float], right_bicep_angle: Optional[float],
    elbow_torso_result: Tuple[Optional[float], Optional[float], Optional[float], str], 
    hip_shoulder_angle: Optional[float],
    difficulty: str = 'NORMAL'  # NEW PARAMETER
) -> Tuple[int, List[str]]:
    
    diff_settings = getattr(BicepCurlDifficulty, difficulty.upper(), BicepCurlDifficulty.NORMAL)
    
    # ... existing code ...
    
    # MODIFIED: Use difficulty settings
    if self.bicep_curl_state == BicepCurlState.CURL_START and active_bicep_angle < diff_settings['curl_up_threshold']:
        if self.state_enter_time is not None:
            duration = time.time() - self.state_enter_time
            
            # NEW: Check tempo
            tempo_valid, tempo_msg = self.check_curl_tempo(duration, 'concentric', difficulty)
            if not tempo_valid and tempo_msg:
                self.bicep_curl_feedback_manager.add_feedback(tempo_msg, FeedbackPriority.MEDIUM)
                self.pending_rep_valid = False
        
        self.bicep_curl_state = BicepCurlState.CURL_UP
        # ... rest of code ...
    
    elif self.bicep_curl_state == BicepCurlState.CURL_UP and active_bicep_angle > diff_settings['curl_down_threshold']:
        if self.state_enter_time is not None:
            duration = time.time() - self.state_enter_time
            
            # NEW: Check eccentric tempo
            tempo_valid, tempo_msg = self.check_curl_tempo(duration, 'eccentric', difficulty)
            if not tempo_valid and tempo_msg:
                self.bicep_curl_feedback_manager.add_feedback(tempo_msg, FeedbackPriority.MEDIUM)
                # Don't invalidate rep for eccentric tempo, just warn
        
        # ... rest of code ...
```

---

## CẢI THIỆN 3: SHOULDER FLEXION (Độ ưu tiên: CRITICAL)

### Vấn đề hiện tại:
```python
elbow_not_straight = 140°       # QUÁ LỎI LẺO!
flex_up_threshold = 110°        # Chưa đủ cao
# Thiếu kiểm tra shoulder elevation
```

### Giải pháp đề xuất:

#### Bước 1: Fix elbow threshold
```python
class ShoulderFlexionDifficulty:
    EASY = {
        'flex_start_threshold': 20,
        'flex_up_threshold': 100,
        'flex_down_threshold': 35,
        'elbow_not_straight': 155,  # Lỏng hơn cho người già
        'max_shoulder_elevation': 0.08
    }
    
    NORMAL = {
        'flex_start_threshold': 15,
        'flex_up_threshold': 130,
        'flex_down_threshold': 30,
        'elbow_not_straight': 165,  # Chặt hơn nhiều!
        'max_shoulder_elevation': 0.05
    }
    
    HARD = {
        'flex_start_threshold': 10,
        'flex_up_threshold': 150,
        'flex_down_threshold': 25,
        'elbow_not_straight': 170,  # Gần như thẳng hoàn toàn
        'max_shoulder_elevation': 0.03
    }
```

#### Bước 2: Thêm shoulder elevation check
```python
def check_shoulder_elevation(self, shoulder: Landmark, 
                            start_shoulder_y: Optional[float],
                            difficulty: str = 'NORMAL') -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra vai có nhún lên không (shoulder shrugging)
    Vai nên cố định khi nâng tay
    """
    if start_shoulder_y is None:
        return True, None
    
    diff_settings = getattr(ShoulderFlexionDifficulty, difficulty.upper(), ShoulderFlexionDifficulty.NORMAL)
    
    elevation = abs(shoulder.y - start_shoulder_y)
    
    if elevation > diff_settings['max_shoulder_elevation']:
        return False, "Giữ vai xuống, không nhún vai!"
    
    return True, None
```

#### Bước 3: Thêm wrist height check
```python
def check_wrist_height(self, wrist: Landmark, elbow: Landmark, 
                      state: int) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra cổ tay có cao hơn khuỷu không khi ở UP state
    """
    if state != ShoulderFlexionState.FLEXION_UP:
        return True, None
    
    # y càng nhỏ càng cao (screen coordinates)
    if wrist.y > elbow.y - 0.02:  # Wrist phải cao hơn elbow ít nhất 2%
        return False, "Nâng cổ tay cao hơn khuỷu!"
    
    return True, None
```

#### Bước 4: Cải thiện _process_single_arm_flexion
```python
def _process_single_arm_flexion(
    self,
    flexion_angle: Optional[float],
    elbow_angle: Optional[float],
    arm_state: int,
    arm_enter_time: Optional[float],
    arm_valid: bool,
    arm_straight_valid: bool,
    elbow_angles_list: List[float],
    arm_name: str,
    shoulder: Landmark,  # NEW
    wrist: Landmark,     # NEW
    elbow: Landmark,     # NEW
    start_shoulder_y: Optional[float],  # NEW
    difficulty: str = 'NORMAL'  # NEW
) -> Tuple[int, Optional[float], bool, bool, List[float], Optional[float]]:  # Added return for shoulder_y
    
    diff_settings = getattr(ShoulderFlexionDifficulty, difficulty.upper(), ShoulderFlexionDifficulty.NORMAL)
    
    # ... existing code ...
    
    # MODIFIED: Use difficulty settings for elbow check
    if arm_state in [ShoulderFlexionState.FLEXION_START, ShoulderFlexionState.FLEXION_UP, ShoulderFlexionState.FLEXION_DOWN]:
        if elbow_angle is not None:
            elbow_angles_list.append(elbow_angle)
            if len(elbow_angles_list) > 3:
                elbow_angles_list.pop(0)
            avg_elbow = sum(elbow_angles_list) / len(elbow_angles_list) if elbow_angles_list else elbow_angle
            
            if avg_elbow is not None and avg_elbow < diff_settings['elbow_not_straight']:
                self.shoulder_flexion_feedback_manager.add_feedback(f"Thẳng tay {arm_name} ra!", FeedbackPriority.HIGH)
                arm_straight_valid = False
            else:
                arm_straight_valid = True
        
        # NEW: Check shoulder elevation
        shoulder_valid, shoulder_msg = self.check_shoulder_elevation(shoulder, start_shoulder_y, difficulty)
        if not shoulder_valid and shoulder_msg:
            self.shoulder_flexion_feedback_manager.add_feedback(shoulder_msg, FeedbackPriority.HIGH)
            arm_valid = False
        
        # NEW: Check wrist height
        wrist_valid, wrist_msg = self.check_wrist_height(wrist, elbow, arm_state)
        if not wrist_valid and wrist_msg:
            self.shoulder_flexion_feedback_manager.add_feedback(wrist_msg, FeedbackPriority.MEDIUM)
    
    # State transitions
    if arm_state == ShoulderFlexionState.IDLE and flexion_angle > diff_settings['flex_start_threshold']:
        arm_state = ShoulderFlexionState.FLEXION_START
        arm_enter_time = time.time()
        arm_valid = True
        arm_straight_valid = True
        elbow_angles_list = []
        start_shoulder_y = shoulder.y  # NEW: Track starting shoulder position
        self.shoulder_flexion_feedback_manager.start_new_rep()
    
    # ... rest of existing code with difficulty settings ...
    
    return arm_state, arm_enter_time, arm_valid, arm_straight_valid, elbow_angles_list, start_shoulder_y
```

---

## CẢI THIỆN 4: KNEE RAISE (Độ ưu tiên: MEDIUM)

### Vấn đề hiện tại:
```python
knee_raise_leg_threshold = 140°     # Có thể quá khó cho người già
knee_raise_arm_threshold = 80°      # Có thể quá khó
sync_delay_max = 0.8s               # Hơi dài
# Thiếu balance check
# Thiếu standing leg stability check
```

### Giải pháp đề xuất:

#### Bước 1: Thêm difficulty levels
```python
class KneeRaiseDifficulty:
    EASY = {
        'leg_threshold': 150,       # Nâng chân thấp hơn
        'arm_threshold': 60,        # Nâng tay thấp hơn
        'start_leg_threshold': 160,
        'start_arm_threshold': 40,
        'sync_delay_max': 1.2,      # Sync lỏng hơn
        'max_hip_tilt': 0.12,       # Cho phép nghiêng nhiều hơn
        'min_standing_knee': 150    # Chân đứng có thể gập nhẹ
    }
    
    NORMAL = {
        'leg_threshold': 140,
        'arm_threshold': 80,
        'start_leg_threshold': 150,
        'start_arm_threshold': 30,
        'sync_delay_max': 0.8,
        'max_hip_tilt': 0.08,
        'min_standing_knee': 160
    }
    
    HARD = {
        'leg_threshold': 120,       # Nâng chân cao hơn
        'arm_threshold': 100,       # Nâng tay cao hơn
        'start_leg_threshold': 165,
        'start_arm_threshold': 20,
        'sync_delay_max': 0.5,      # Sync chặt hơn
        'max_hip_tilt': 0.05,       # Ít nghiêng hơn
        'min_standing_knee': 165    # Chân đứng phải thẳng
    }
```

#### Bước 2: Thêm balance check
```python
def check_balance(self, left_hip: Landmark, right_hip: Landmark,
                 difficulty: str = 'NORMAL') -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra thăng bằng khi nâng chân (hip không nghiêng quá)
    """
    diff_settings = getattr(KneeRaiseDifficulty, difficulty.upper(), KneeRaiseDifficulty.NORMAL)
    
    hip_tilt = abs(left_hip.y - right_hip.y)
    
    if hip_tilt > diff_settings['max_hip_tilt']:
        return False, "Giữ thăng bằng, hông thẳng!"
    
    return True, None
```

#### Bước 3: Thêm standing leg check
```python
def check_standing_leg(self, standing_knee_angle: Optional[float],
                      difficulty: str = 'NORMAL') -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra chân đứng có thẳng không
    """
    if standing_knee_angle is None:
        return True, None
    
    diff_settings = getattr(KneeRaiseDifficulty, difficulty.upper(), KneeRaiseDifficulty.NORMAL)
    
    if standing_knee_angle < diff_settings['min_standing_knee']:
        return False, "Chân đứng phải thẳng!"
    
    return True, None
```

#### Bước 4: Cải thiện process_knee_raise
```python
def process_knee_raise(
    self,
    left_hip: Landmark, left_knee: Landmark, left_ankle: Landmark,
    right_hip: Landmark, right_knee: Landmark, right_ankle: Landmark,
    left_shoulder: Landmark, left_wrist: Landmark,
    right_shoulder: Landmark, right_wrist: Landmark,
    left_knee_angle: Optional[float], right_knee_angle: Optional[float],
    left_flexion_angle: Optional[float], right_flexion_angle: Optional[float],
    hip_shoulder_angle: Optional[float],
    difficulty: str = 'NORMAL'  # NEW PARAMETER
) -> Tuple[int, List[str]]:
    
    diff_settings = getattr(KneeRaiseDifficulty, difficulty.upper(), KneeRaiseDifficulty.NORMAL)
    
    # ... existing smoothing code ...
    
    # NEW: Check balance
    balance_valid, balance_msg = self.check_balance(left_hip, right_hip, difficulty)
    if not balance_valid and balance_msg:
        self.knee_raise_feedback_manager.add_feedback(balance_msg, FeedbackPriority.HIGH)
        self.pair_valid = False
    
    # NEW: Check standing leg
    if active_pair == 'left_leg_right_arm':
        standing_knee = avg_right_knee
    elif active_pair == 'right_leg_left_arm':
        standing_knee = avg_left_knee
    else:
        standing_knee = None
    
    if standing_knee is not None:
        standing_valid, standing_msg = self.check_standing_leg(standing_knee, difficulty)
        if not standing_valid and standing_msg:
            self.knee_raise_feedback_manager.add_feedback(standing_msg, FeedbackPriority.MEDIUM)
    
    # ... existing code with difficulty settings ...
    
    # MODIFIED: Use difficulty settings
    if self.knee_raise_state == KneeRaiseState.RAISE_START:
        leg_raised = leg_angle < diff_settings['leg_threshold']
        arm_raised = arm_angle > diff_settings['arm_threshold']
        
        # ... rest of code ...
```

---

## CẢI THIỆN 5: HỆ THỐNG CHUNG

### 5.1. Thêm Rep Quality Score

```python
class RepQualityScorer:
    """
    Đánh giá chất lượng rep từ 0-100%
    """
    
    @staticmethod
    def calculate_squat_quality(
        knee_angle_min: float,
        hip_drop: float,
        knee_symmetry: float,
        back_angle: float,
        hold_time: float,
        difficulty: str = 'NORMAL'
    ) -> Tuple[int, str]:
        """
        Returns: (score, grade)
        """
        score = 100
        
        # Depth score (40 points)
        if knee_angle_min > 100:
            score -= 40
        elif knee_angle_min > 90:
            score -= 20
        elif knee_angle_min > 80:
            score -= 10
        
        # Hip drop score (20 points)
        if hip_drop < 0.05:
            score -= 20
        elif hip_drop < 0.08:
            score -= 10
        
        # Symmetry score (20 points)
        if knee_symmetry > 30:
            score -= 20
        elif knee_symmetry > 15:
            score -= 10
        
        # Back angle score (10 points)
        if back_angle < 10 or back_angle > 45:
            score -= 10
        elif back_angle < 15 or back_angle > 40:
            score -= 5
        
        # Hold time score (10 points)
        if hold_time < 0.2:
            score -= 10
        elif hold_time < 0.3:
            score -= 5
        
        # Grade
        if score >= 90:
            grade = "XUẤT SẮC"
        elif score >= 75:
            grade = "TỐT"
        elif score >= 60:
            grade = "KHÁ"
        else:
            grade = "CẦN CẢI THIỆN"
        
        return max(0, score), grade
```

### 5.2. Thêm Progressive Difficulty

```python
class ProgressiveTraining:
    """
    Tự động điều chỉnh độ khó dựa trên performance
    """
    
    def __init__(self):
        self.rep_history = []
        self.current_difficulty = 'EASY'
        self.consecutive_good_reps = 0
        self.consecutive_bad_reps = 0
    
    def update(self, rep_quality_score: int):
        """
        Update difficulty based on rep quality
        """
        self.rep_history.append(rep_quality_score)
        
        if rep_quality_score >= 75:
            self.consecutive_good_reps += 1
            self.consecutive_bad_reps = 0
        else:
            self.consecutive_bad_reps += 1
            self.consecutive_good_reps = 0
        
        # Tăng độ khó sau 10 reps tốt liên tiếp
        if self.consecutive_good_reps >= 10:
            if self.current_difficulty == 'EASY':
                self.current_difficulty = 'NORMAL'
                self.consecutive_good_reps = 0
                return "Tăng độ khó lên NORMAL!"
            elif self.current_difficulty == 'NORMAL':
                self.current_difficulty = 'HARD'
                self.consecutive_good_reps = 0
                return "Tăng độ khó lên HARD!"
        
        # Giảm độ khó sau 5 reps kém liên tiếp
        if self.consecutive_bad_reps >= 5:
            if self.current_difficulty == 'HARD':
                self.current_difficulty = 'NORMAL'
                self.consecutive_bad_reps = 0
                return "Giảm độ khó xuống NORMAL"
            elif self.current_difficulty == 'NORMAL':
                self.current_difficulty = 'EASY'
                self.consecutive_bad_reps = 0
                return "Giảm độ khó xuống EASY"
        
        return None
    
    def get_current_difficulty(self) -> str:
        return self.current_difficulty
```

### 5.3. Cải thiện Feedback Messages

```python
class FeedbackTranslator:
    """
    Dịch feedback thành tiếng Việt rõ ràng hơn
    """
    
    FEEDBACK_MAP = {
        # Squat
        "Deeper hip bend!": "Gập hông sâu hơn, đẩy mông ra sau!",
        "Even squat": "Hai chân đều nhau!",
        "Lower hips!": "Hạ hông xuống thấp hơn!",
        "Keep hips bent!": "Giữ hông gập, đừng đứng thẳng!",
        "Lean forward": "Nghiêng người về phía trước một chút!",
        "Less lean": "Đứng thẳng lưng hơn!",
        
        # Bicep Curl
        "Duỗi thẳng tay": "Duỗi thẳng tay hoàn toàn xuống!",
        "Gập cao hơn": "Gập tay lên cao hơn, chạm vai!",
        "Nắm chặt tay, xoay vào trong!": "Nắm chặt tay, xoay cổ tay vào trong!",
        "Khép khuỷu tay lại!": "Giữ khuỷu tay sát thân!",
        "Đừng đung đưa người": "Đứng yên, không đung đưa!",
        "Giữ vai cố định": "Vai không nhúc nhích!",
        
        # Shoulder Flexion
        "Tay trái cao hơn": "Nâng tay trái lên cao hơn, qua đầu!",
        "Tay phải cao hơn": "Nâng tay phải lên cao hơn, qua đầu!",
        "Thẳng tay left ra!": "Duỗi thẳng tay trái!",
        "Thẳng tay right ra!": "Duỗi thẳng tay phải!",
        "Thẳng lưng lên": "Đứng thẳng lưng!",
        
        # Knee Raise
        "Knee higher": "Nâng đầu gối cao hơn!",
        "Arm higher": "Giơ tay cao hơn!",
        "Balance": "Giữ thăng bằng!",
        "Arm now": "Giơ tay lên ngay!",
        "Knee now": "Nâng đầu gối lên ngay!",
    }
    
    @staticmethod
    def translate(feedback: str) -> str:
        return FeedbackTranslator.FEEDBACK_MAP.get(feedback, feedback)
```

---

## IMPLEMENTATION PLAN

### Phase 1: Critical Fixes (Week 1)
**Mục tiêu**: Fix các vấn đề nghiêm trọng nhất

- [ ] **Day 1-2**: Implement Squat improvements
  - Add difficulty levels
  - Add knee alignment check
  - Add knee valgus check
  - Test với real users
  
- [ ] **Day 3-4**: Implement Shoulder Flexion improvements
  - Fix elbow threshold
  - Add shoulder elevation check
  - Add wrist height check
  - Test với real users
  
- [ ] **Day 5**: Integration testing
  - Test all exercises
  - Fix bugs
  - Collect user feedback

### Phase 2: Important Improvements (Week 2)
**Mục tiêu**: Thêm các tính năng quan trọng

- [ ] **Day 1-2**: Implement Bicep Curl improvements
  - Add difficulty levels
  - Add tempo control
  - Test với real users
  
- [ ] **Day 3-4**: Implement Knee Raise improvements
  - Add difficulty levels
  - Add balance check
  - Add standing leg check
  - Test với real users
  
- [ ] **Day 5**: Integration testing
  - Test all exercises
  - Fine-tune thresholds
  - Collect user feedback

### Phase 3: Enhancements (Week 3-4)
**Mục tiêu**: Thêm các tính năng nâng cao

- [ ] **Week 3**: Rep Quality Scoring
  - Implement scoring system
  - Add UI display
  - Test và fine-tune
  
- [ ] **Week 4**: Progressive Training
  - Implement auto difficulty adjustment
  - Add achievement system
  - Final testing

---

## TESTING CHECKLIST

### Unit Tests
- [ ] Test Squat với different knee angles
- [ ] Test Squat với different hip drops
- [ ] Test Bicep Curl với different elbow positions
- [ ] Test Shoulder Flexion với different elbow angles
- [ ] Test Knee Raise với different balance scenarios

### Integration Tests
- [ ] Test với real video footage
- [ ] Test với different camera angles
- [ ] Test với different lighting conditions
- [ ] Test với different user heights/body types

### User Acceptance Tests
- [ ] Test với người già (70+ tuổi)
- [ ] Test với người trung niên (40-60 tuổi)
- [ ] Test với người trẻ (20-40 tuổi)
- [ ] Collect feedback về độ khó
- [ ] Measure accuracy vs manual count

---

## ROLLBACK PLAN

Nếu có vấn đề sau khi deploy:

1. **Immediate rollback**: Revert về version cũ
2. **Investigate**: Tìm hiểu nguyên nhân
3. **Fix**: Sửa lỗi trong dev environment
4. **Re-test**: Test kỹ lưỡng
5. **Re-deploy**: Deploy lại với fix

---

## SUCCESS METRICS

### Accuracy
- [ ] Squat counting accuracy >= 95%
- [ ] Bicep Curl counting accuracy >= 95%
- [ ] Shoulder Flexion counting accuracy >= 90%
- [ ] Knee Raise counting accuracy >= 90%

### User Satisfaction
- [ ] User feedback score >= 4/5
- [ ] Completion rate >= 80%
- [ ] Return rate >= 70%

### Performance
- [ ] Processing time < 200ms per frame
- [ ] No frame drops
- [ ] Smooth feedback display

---

## NOTES

- Tất cả thay đổi phải backward compatible
- Phải test kỹ trước khi deploy
- Phải có rollback plan
- Phải collect user feedback
- Phải measure success metrics
