# src/aircontrol/gestures/volume_gesture.py

import math
import time
from dataclasses import dataclass

from aircontrol.gestures.features import center_of_mass


@dataclass(frozen=True)
class VolumeSignal:
    direction: str  # "up" | "down"
    steps: int      # how many step units to apply this tick


class VolumeGesture:
    """
    Horizontal hand = volume mode.
    Move hand up/down (relative to baseline) = volume up/down.
    Changes happen at a controlled rate (ticks_per_sec).
    """

    INDEX_MCP = 5
    PINKY_MCP = 17

    def __init__(
        self,
        angle_deg_thresh: float = 20.0,   
        y_deadband: float = 0.03,         
        ticks_per_sec: float = 8.0,       
        max_steps_per_tick: int = 3,      
        gain: float = 60.0,               
    ):
        self.angle_thresh = math.radians(angle_deg_thresh)
        self.y_deadband = y_deadband
        self.tick_dt = 1.0 / ticks_per_sec
        self.max_steps_per_tick = max_steps_per_tick
        self.gain = gain

        self._baseline_y = None
        self._last_tick = 0.0

    def _is_horizontal(self, hand_landmarks) -> bool:
        lms = hand_landmarks.landmark
        a = lms[self.INDEX_MCP]
        b = lms[self.PINKY_MCP]

        dx = b.x - a.x
        dy = b.y - a.y
        angle = abs(math.atan2(dy, dx))  # 0 = perfectly horizontal

        return angle < self.angle_thresh

    def update(self, hand_landmarks):
        """
        Returns:
          VolumeSignal or None
        """
        now = time.time()

        if not self._is_horizontal(hand_landmarks):
            self._baseline_y = None
            return None

        norm_pt, _ = center_of_mass(hand_landmarks)
        if self._baseline_y is None:
            self._baseline_y = norm_pt.y
            self._last_tick = now
            return None

        if now - self._last_tick < self.tick_dt:
            return None
        self._last_tick = now

        dy = self._baseline_y - norm_pt.y  # positive if hand moved UP

        if abs(dy) < self.y_deadband:
            return None

        steps = int(min(self.max_steps_per_tick, max(1, abs(dy) * self.gain)))

        if dy > 0:
            return VolumeSignal(direction="up", steps=steps)
        else:
            return VolumeSignal(direction="down", steps=steps)