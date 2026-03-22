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
    FLEXION_START = 1
    FLEXION_UP = 2
    FLEXION_DOWN = 3

class KneeRaiseState:
    IDLE = 0
    RAISE_START = 1
    RAISE_UP = 2
    RAISE_DOWN = 3

class FeedbackPriority:
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Landmark:
    def __init__(self, x: float, y: float, z: float = 0, visibility: float = 0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility
