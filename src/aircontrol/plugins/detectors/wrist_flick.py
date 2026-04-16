# src/aircontrol/plugins/detectors/wrist_flick.py

from __future__ import annotations

from collections import deque
from typing import Deque, Optional

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    WRIST,
    INDEX_MCP,
    MIDDLE_MCP,
    RING_MCP,
    PINKY_MCP,
    INDEX_TIP,
    INDEX_PIP,
    MIDDLE_TIP,
    MIDDLE_PIP,
    RING_TIP,
    RING_PIP,
    PINKY_TIP,
    PINKY_PIP,
)


class WristFlickDetector:
    """
    Open-palm + horizontal wrist/hand flick detector.

    Gesture gate:
      - all four fingers extended
      - hand anchor tracked over recent frames

    Trigger:
      - quick horizontal motion of the hand anchor
      - horizontal motion must dominate vertical motion

    Emits:
      - gesture.wrist_flick_right
      - gesture.wrist_flick_left
    """

    def __init__(
        self,
        hold_frames: int = 2,
        cooldown_frames: int = 10,
        history_len: int = 4,
        flick_dx_threshold: float = 0.08,
        instant_dx_threshold: float = 0.025,
        max_total_dy: float = 0.05,
        min_finger_extension: float = 0.02,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.history_len = int(history_len)

        self.flick_dx_threshold = float(flick_dx_threshold)
        self.instant_dx_threshold = float(instant_dx_threshold)
        self.max_total_dy = float(max_total_dy)
        self.min_finger_extension = float(min_finger_extension)

        self._hold_counter = 0
        self._cooldown = 0
        self._armed = False
        self._x_history: Deque[float] = deque(maxlen=self.history_len)
        self._y_history: Deque[float] = deque(maxlen=self.history_len)

    def _reset(self) -> None:
        self._hold_counter = 0
        self._armed = False
        self._x_history.clear()
        self._y_history.clear()

    def _finger_extended(self, lms, tip_id: int, pip_id: int) -> bool:
        # In image coordinates, smaller y means higher on screen.
        return lms[tip_id].y < lms[pip_id].y - self.min_finger_extension

    def _is_open_palm(self, lms) -> bool:
        return (
            self._finger_extended(lms, INDEX_TIP, INDEX_PIP)
            and self._finger_extended(lms, MIDDLE_TIP, MIDDLE_PIP)
            and self._finger_extended(lms, RING_TIP, RING_PIP)
            and self._finger_extended(lms, PINKY_TIP, PINKY_PIP)
        )

    def _hand_anchor(self, lms) -> tuple[float, float]:
        # Stable anchor using wrist + MCPs rather than fingertip positions.
        x = (
            lms[WRIST].x
            + lms[INDEX_MCP].x
            + lms[MIDDLE_MCP].x
            + lms[RING_MCP].x
            + lms[PINKY_MCP].x
        ) / 5.0
        y = (
            lms[WRIST].y
            + lms[INDEX_MCP].y
            + lms[MIDDLE_MCP].y
            + lms[RING_MCP].y
            + lms[PINKY_MCP].y
        ) / 5.0
        return x, y

    def _detect_flick(self) -> Optional[str]:
        if len(self._x_history) < 3 or len(self._y_history) < 3:
            return None

        xs = list(self._x_history)
        ys = list(self._y_history)

        total_dx = xs[-1] - xs[0]
        last_dx = xs[-1] - xs[-2]
        total_dy = abs(ys[-1] - ys[0])

        # Require:
        # 1) enough total horizontal movement
        # 2) recent motion still continuing in same direction
        # 3) vertical drift not too large
        if total_dy > self.max_total_dy:
            return None

        if total_dx >= self.flick_dx_threshold and last_dx >= self.instant_dx_threshold:
            return "right"

        if total_dx <= -self.flick_dx_threshold and last_dx <= -self.instant_dx_threshold:
            return "left"

        return None

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._reset()
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        if not self._is_open_palm(lms):
            self._reset()
            return []

        anchor_x, anchor_y = self._hand_anchor(lms)

        # Arm only after briefly holding open palm
        if not self._armed:
            self._hold_counter += 1
            self._x_history.clear()
            self._y_history.clear()
            self._x_history.append(anchor_x)
            self._y_history.append(anchor_y)

            if self._hold_counter >= self.hold_frames:
                self._armed = True

            return []

        # Once armed, track recent anchor positions
        self._x_history.append(anchor_x)
        self._y_history.append(anchor_y)

        direction = self._detect_flick()
        if direction == "right":
            self._cooldown = self.cooldown_frames
            self._reset()
            return [GestureEvent("gesture.wrist_flick_right", {})]

        if direction == "left":
            self._cooldown = self.cooldown_frames
            self._reset()
            return [GestureEvent("gesture.wrist_flick_left", {})]

        return []


class WristFlickPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[WristFlickDetector()], actions={})


def plugin():
    return WristFlickPlugin()