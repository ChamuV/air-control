# src/aircontrol/plugins/detectors/call_sign.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    THUMB_IP,
    PINKY_MCP,
    PINKY_PIP,
    PINKY_DIP,
    PINKY_TIP,
)


class CallSignDetector:
    def __init__(
        self,
        hold_frames: int = 4,
        cooldown_frames: int = 12,
        min_gesture_frames: int = 2,
        thumb_x_tol: float = 0.07,
        thumb_y_span: float = 0.07,
        pinky_y_tol: float = 0.07,
        pinky_x_span: float = 0.06,
    ):
        self.hold_frames = hold_frames
        self.cooldown_frames = cooldown_frames
        self.min_gesture_frames = min_gesture_frames

        self.thumb_x_tol = thumb_x_tol
        self.thumb_y_span = thumb_y_span
        self.pinky_y_tol = pinky_y_tol
        self.pinky_x_span = pinky_x_span

        self._hold_counter = 0
        self._cooldown = 0
        self._gesture_streak = 0

    def _thumb_up(self, lms):
        ids = [1, 2, THUMB_IP, THUMB_TIP]
        xs = [lms[i].x for i in ids]
        ys = [lms[i].y for i in ids]

        vertical = (max(xs) - min(xs)) < self.thumb_x_tol
        span = (ys[0] - ys[-1]) > self.thumb_y_span

        return vertical and span

    def _pinky_side(self, lms):
        ids = [PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP]
        xs = [lms[i].x for i in ids]
        ys = [lms[i].y for i in ids]

        horizontal = (max(ys) - min(ys)) < self.pinky_y_tol
        span = (max(xs) - min(xs)) > self.pinky_x_span

        return horizontal and span

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._hold_counter = 0
            self._cooldown = 0
            self._gesture_streak = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        thumb_ok = self._thumb_up(lms)
        pinky_ok = self._pinky_side(lms)

        gesture = thumb_ok and pinky_ok

        if not gesture:
            self._hold_counter = 0
            self._gesture_streak = 0
            return []

        self._gesture_streak += 1
        if self._gesture_streak < self.min_gesture_frames:
            return []

        self._hold_counter += 1

        if self._hold_counter >= self.hold_frames:
            self._hold_counter = 0
            self._gesture_streak = 0
            self._cooldown = self.cooldown_frames
            return [
                GestureEvent(
                    "gesture.call_sign",
                    {
                        "number": "+919845103831",
                        "mode": "video",
                    },
                )
            ]

        return []


class CallSignPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[CallSignDetector()], actions={})


def plugin():
    return CallSignPlugin()