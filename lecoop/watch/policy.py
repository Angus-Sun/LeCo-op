"""
script for watch: random button combo that's held for random number of steps before
picking a new one. Didn't do for all buttons individually cuz too lazy
"""

import numpy as np

MIN_STICK_STEPS = 10
MAX_STICK_STEPS = 40

class StickyRandomPolicy:
    def __init__(self, rng: np.random.Generator):
        self._rng = rng
        self._current_actions = self._sample_actions()
        self._steps_left = self._sample_stick_duration()

    def _sample_actions(self) -> np.ndarray:
        return self._rng.integers(0, 2, size=(2, 3))

    def _sample_stick_duration(self) -> int:
        return int(self._rng.integers(MIN_STICK_STEPS, MAX_STICK_STEPS + 1))

    def next_actions(self) -> np.ndarray:
        if self._steps_left <= 0:
            self._current_actions = self._sample_actions()
            self._steps_left = self._sample_stick_duration()
        self._steps_left -= 1
        return self._current_actions
