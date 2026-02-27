# src/aircontrol/gestures/window_gesture.py

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class WindowSignal:
    direction: str  # "left" | "right"


class WindowMotionGesture:
    """
    Vertical palm (pinky x spread small) enables window switching.
    Horizontal motion (x velocity) triggers left/right switch.
    """

    PINKY_IDS = (17, 18, 19, 20)
    TRACK_IDS = (0, 5, 9, 13, 17)

    def __init__(
        self,
        pinky_x_spread_thresh: float = 0.03,
        x_deadband: float = 0.04,
        tick_dt: float = 0.5,     # slower than volume
    ):
        self.pinky_x_spread_thresh = pinky_x_spread_thresh
        self.x_deadband = x_deadband
        self.tick_dt = tick_dt

        self._baseline_x = None
        self._last_tick = 0.0

    def reset(self):
        self._baseline_x = None

    def _vertical_palm(self, hand_landmarks):
        lms = hand_landmarks.landmark
        xs = [lms[i].x for i in self.PINKY_IDS]
        spread = max(xs) - min(xs)
        return spread < self.pinky_x_spread_thresh

    def _avg_x(self, hand_landmarks):
        lms = hand_landmarks.landmark
        xs = [lms[i].x for i in self.TRACK_IDS]
        return sum(xs) / len(xs)

    def update(self, hand_landmarks):
        now = time.time()

        if not self._vertical_palm(hand_landmarks):
            self.reset()
            return None

        x = self._avg_x(hand_landmarks)

        if self._baseline_x is None:
            self._baseline_x = x
            self._last_tick = now
            return None

        if now - self._last_tick < self.tick_dt:
            return None

        dx = x - self._baseline_x

        if abs(dx) < self.x_deadband:
            return None

        self._last_tick = now
        self._baseline_x = x

        if dx < 0:
            return WindowSignal(direction="right")
        else:
            return WindowSignal(direction="left")