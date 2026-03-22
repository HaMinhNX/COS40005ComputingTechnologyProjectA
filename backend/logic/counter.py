from typing import List, Tuple
from .strategies.squat import SquatStrategy
from .strategies.bicep_curl import BicepCurlStrategy
from .strategies.shoulder_flexion import ShoulderFlexionStrategy
from .strategies.knee_raise import KneeRaiseStrategy

class ExerciseCounter:
    def __init__(self):
        self.strategies = {
            'squat': SquatStrategy(),
            'bicep-curl': BicepCurlStrategy(),
            'shoulder-flexion': ShoulderFlexionStrategy(),
            'knee-raise': KneeRaiseStrategy()
        }
        self.total_reps = 0

    @property
    def squat_counter(self): return self.strategies['squat'].counter
    @property
    def curl_counter(self): return self.strategies['bicep-curl'].counter
    @property
    def shoulder_flexion_counter(self): return self.strategies['shoulder-flexion'].counter
    @property
    def knee_raise_counter(self): return self.strategies['knee-raise'].counter

    @property
    def squat_state(self): return self.strategies['squat'].state
    @property
    def bicep_curl_state(self): return self.strategies['bicep-curl'].state
    @property
    def shoulder_flexion_state(self): return self.strategies['shoulder-flexion'].state
    @property
    def knee_raise_state(self): return self.strategies['knee-raise'].state

    def reset_state(self, exercise_name: str):
        if exercise_name in self.strategies:
            self.strategies[exercise_name].reset()
        self.total_reps = sum(s.counter for s in self.strategies.values())

    def process_bicep_curl(self, **kwargs) -> Tuple[int, List[str]]:
        # For backward compatibility with existing router calls
        # We extract landmarks from kwargs or just call the strategy with specific props
        # In a real refactor, we'd pass landmarks and pre-calculated angles
        return self.strategies['bicep-curl'].process(kwargs.get('landmarks', []), kwargs)

    def process_squat(self, **kwargs) -> Tuple[int, List[str]]:
        return self.strategies['squat'].process(kwargs.get('landmarks', []), kwargs)

    def process_shoulder_flexion(self, **kwargs) -> Tuple[int, List[str]]:
        return self.strategies['shoulder-flexion'].process(kwargs.get('landmarks', []), kwargs)

    def process_knee_raise(self, **kwargs) -> Tuple[int, List[str]]:
        return self.strategies['knee-raise'].process(kwargs.get('landmarks', []), kwargs)

    def update_total_reps(self):
        self.total_reps = sum(s.counter for s in self.strategies.values())
