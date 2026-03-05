# src/aircontrol/plugins/detectors/horizontal_yo.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    THUMB_IP,
    INDEX_TIP,
    INDEX_PIP,
    INDEX_MCP,
    MIDDLE_TIP,
    MIDDLE_PIP,
    RING_TIP,
    RING_PIP,
    PINKY_TIP,
    PINKY_PIP,
    PINKY_MCP,
)


class HorizontalYoDetector:
    """
    Gesture: "horizontal_yo"
      - Thumb up
      - Index horizontal (TIP/PIP/MCP ~ same y) AND not vertical-ish
      - Pinky horizontal (TIP/PIP/MCP ~ same y) AND not vertical-ish
      - Middle + ring folded
    Hold for N frames to trigger.

    Emits: gesture.horizontal_yo
    """

    def __init__(
        self,
        hold_frames: int = 4,
        cooldown_frames: int = 5,
        sideways_y_tol: float = 0.02,
        min_x_span: float = 0.02,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.sideways_y_tol = float(sideways_y_tol)
        self.min_x_span = float(min_x_span)

        self._hold = 0
        self._cooldown = 0

    def _horizontal_triplet(self, tip, pip, mcp) -> bool:
        # "horizontal" ≈ y values close (aligned horizontally)
        y_ok = (abs(tip.y - pip.y) < self.sideways_y_tol) and (abs(pip.y - mcp.y) < self.sideways_y_tol)
        # also require some x spread so it isn't a near-vertical stack
        x_span = max(tip.x, pip.x, mcp.x) - min(tip.x, pip.x, mcp.x)
        x_ok = x_span >= self.min_x_span
        return y_ok and x_ok

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._hold = 0
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        thumb_up = lms[THUMB_TIP].y < lms[THUMB_IP].y

        index_horizontal = self._horizontal_triplet(
            lms[INDEX_TIP], lms[INDEX_PIP], lms[INDEX_MCP]
        )
        pinky_horizontal = self._horizontal_triplet(
            lms[PINKY_TIP], lms[PINKY_PIP], lms[PINKY_MCP]
        )

        middle_folded = lms[MIDDLE_TIP].y > lms[MIDDLE_PIP].y
        ring_folded = lms[RING_TIP].y > lms[RING_PIP].y

        gesture = thumb_up and index_horizontal and pinky_horizontal and middle_folded and ring_folded

        if gesture:
            self._hold += 1
            if self._hold >= self.hold_frames:
                self._hold = 0
                self._cooldown = self.cooldown_frames
                return [GestureEvent("gesture.horizontal_yo", {})]
        else:
            self._hold = 0

        return []


class HorizontalYoPlugin:
    """Detector-only plugin."""
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[HorizontalYoDetector()], actions={})


def plugin():
    return HorizontalYoPlugin()