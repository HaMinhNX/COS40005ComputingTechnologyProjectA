from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any
from ..common import Landmark
from ..utils import FeedbackManager

class BaseExerciseStrategy(ABC):
    def __init__(self):
        self.counter = 0
        self.state = 0
        self.feedback_manager = FeedbackManager()
        self.last_process_time = 0

    @abstractmethod
    def process(self, landmarks: List[Landmark], angles: Dict[str, Any]) -> Tuple[int, List[str]]:
        pass

    @abstractmethod
    def reset(self):
        self.counter = 0
        self.state = 0
        self.feedback_manager.clear_feedback()
