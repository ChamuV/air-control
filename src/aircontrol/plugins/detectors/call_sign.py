# src/aircontrol/plugins/detectors/call_sign.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    THUMB_IP,
    INDEX_MCP,
    INDEX_PIP,
    INDEX_TIP,
    MIDDLE_MCP,
    MIDDLE_PIP,
    MIDDLE_TIP,
    RING_MCP,
    RING_PIP,
    RING_TIP,
    PINKY_MCP,
    PINKY_PIP,
    PINKY_DIP,
    PINKY_TIP,
)


class CallSignDetector:
    """
    Call sign:
        thumb up
        pinky sideways
        other fingers folded
    """

    def __init__(
        self,
        hold_frames: int = 6,
        cooldown_frames: int = 10,
        thumb_x_tol: float = 0.035,
        thumb_y_span: float = 0.10,
        pinky_y_tol: float = 0.035,
        pinky_x_span: float = 0.08,
        folded_margin: float = 0.015,
    ):
        self.hold_frames = hold_frames
        self.cooldown_frames = cooldown_frames

        self.thumb_x_tol = thumb_x_tol
        self.thumb_y_span = thumb_y_span
        self.pinky_y_tol = pinky_y_tol
        self.pinky_x_span = pinky_x_span
        self.folded_margin = folded_margin

        self._hold_counter = 0
        self._cooldown = 0

    def _thumb_up(self, lms):
        ids = [1, 2, THUMB_IP, THUMB_TIP]

        xs = [lms[i].x for i in ids]
        ys = [lms[i].y for i in ids]

        vertical = (max(xs) - min(xs)) < self.thumb_x_tol
        monotone = all(ys[i + 1] < ys[i] for i in range(len(ys) - 1))
        span = (ys[0] - ys[-1]) > self.thumb_y_span

        return vertical and monotone and span

    def _pinky_side(self, lms):
        ids = [PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP]

        xs = [lms[i].x for i in ids]
        ys = [lms[i].y for i in ids]

        horizontal = (max(ys) - min(ys)) < self.pinky_y_tol
        span = (max(xs) - min(xs)) > self.pinky_x_span

        mono = (
            all(xs[i + 1] > xs[i] for i in range(len(xs) - 1))
            or all(xs[i + 1] < xs[i] for i in range(len(xs) - 1))
        )

        return horizontal and span and mono

    def _folded(self, lms, mcp, pip, tip):
        tip_below = lms[tip].y > lms[pip].y + self.folded_margin
        pip_low = lms[pip].y >= lms[mcp].y - self.folded_margin
        tip_near = abs(lms[tip].x - lms[mcp].x) < 0.06

        return tip_below and pip_low and tip_near

    def update(self, hand_landmarks) -> list[GestureEvent]:

        if hand_landmarks is None:
            self._hold_counter = 0
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        thumb_ok = self._thumb_up(lms)
        pinky_ok = self._pinky_side(lms)

        index_ok = self._folded(lms, INDEX_MCP, INDEX_PIP, INDEX_TIP)
        middle_ok = self._folded(lms, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP)
        ring_ok = self._folded(lms, RING_MCP, RING_PIP, RING_TIP)

        gesture = thumb_ok and pinky_ok and index_ok and middle_ok and ring_ok

        if gesture:
            self._hold_counter += 1

            if self._hold_counter >= self.hold_frames:
                self._hold_counter = 0
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

        else:
            self._hold_counter = 0

        return []


class CallSignPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[CallSignDetector()], actions={})


def plugin():
    return CallSignPlugin()