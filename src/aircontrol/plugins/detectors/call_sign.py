# src/aircontrol/plugins/detectors/call_sign.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    THUMB_IP,
    INDEX_TIP,
    INDEX_MCP,
    MIDDLE_TIP,
    MIDDLE_MCP,
    RING_TIP,
    RING_MCP,
    PINKY_MCP,
    PINKY_PIP,
    PINKY_DIP,
    PINKY_TIP,
)


class CallSignDetector:
    """
    Call sign detector:
      - thumb extended upward-ish
      - pinky extended sideways-ish
      - index, middle, ring mostly folded

    Emits gesture.call_sign after a short stable hold.
    """

    def __init__(
        self,
        hold_frames: int = 3,
        cooldown_frames: int = 10,
        min_gesture_frames: int = 1,
        thumb_x_tol: float = 0.12,
        thumb_y_span: float = 0.045,
        pinky_y_tol: float = 0.12,
        pinky_x_span: float = 0.035,
        folded_margin: float = 0.02,
        min_folded_fingers: int = 2,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.min_gesture_frames = int(min_gesture_frames)

        self.thumb_x_tol = float(thumb_x_tol)
        self.thumb_y_span = float(thumb_y_span)
        self.pinky_y_tol = float(pinky_y_tol)
        self.pinky_x_span = float(pinky_x_span)
        self.folded_margin = float(folded_margin)
        self.min_folded_fingers = int(min_folded_fingers)

        self._hold_counter = 0
        self._cooldown = 0
        self._gesture_streak = 0

    def _thumb_up(self, lms) -> bool:
        ids = [1, 2, THUMB_IP, THUMB_TIP]
        xs = [lms[i].x for i in ids]
        ys = [lms[i].y for i in ids]

        vertical_enough = (max(xs) - min(xs)) < self.thumb_x_tol
        upward_span = (ys[0] - ys[-1]) > self.thumb_y_span

        return vertical_enough and upward_span

    def _pinky_side(self, lms) -> bool:
        ids = [PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP]
        xs = [lms[i].x for i in ids]
        ys = [lms[i].y for i in ids]

        horizontal_enough = (max(ys) - min(ys)) < self.pinky_y_tol
        sideways_span = (max(xs) - min(xs)) > self.pinky_x_span

        return horizontal_enough and sideways_span

    def _finger_folded(self, lms, tip: int, mcp: int) -> bool:
        return lms[tip].y >= lms[mcp].y + self.folded_margin

    def _count_middle_three_folded(self, lms) -> int:
        return sum([
            self._finger_folded(lms, INDEX_TIP, INDEX_MCP),
            self._finger_folded(lms, MIDDLE_TIP, MIDDLE_MCP),
            self._finger_folded(lms, RING_TIP, RING_MCP),
        ])

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
        folded_count = self._count_middle_three_folded(lms)

        gesture = thumb_ok and pinky_ok and (folded_count >= self.min_folded_fingers)

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