# src/aircontrol/plugins/detectors/index_middle_pinch.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    INDEX_TIP,
    MIDDLE_TIP,
    RING_TIP,
    RING_PIP,
    PINKY_TIP,
    PINKY_PIP,
    dist,
)


class IndexMiddlePinchDetector:
    """
    Gesture:
      - thumb touches index
      - thumb touches middle
      - ring + pinky extended

    Emits: gesture.index_middle_pinch
    """

    def __init__(
        self,
        pinch_threshold: float = 0.04,
        cooldown_frames: int = 8,
    ):
        self.pinch_threshold = float(pinch_threshold)
        self.cooldown_frames = int(cooldown_frames)
        self._cooldown = 0

    def _is_extended(self, lms, tip: int, pip: int) -> bool:
        # smaller y = finger pointing upward in image coordinates
        return lms[tip].y < lms[pip].y

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        d_thumb_index = dist(lms, THUMB_TIP, INDEX_TIP)
        d_thumb_middle = dist(lms, THUMB_TIP, MIDDLE_TIP)

        ring_extended = self._is_extended(lms, RING_TIP, RING_PIP)
        pinky_extended = self._is_extended(lms, PINKY_TIP, PINKY_PIP)

        gesture = (
            d_thumb_index < self.pinch_threshold
            and d_thumb_middle < self.pinch_threshold
            and ring_extended
            and pinky_extended
        )

        if not gesture:
            return []

        self._cooldown = self.cooldown_frames

        return [
            GestureEvent(
                "gesture.index_middle_pinch",
                {"d_ti": d_thumb_index, "d_tm": d_thumb_middle},
            )
        ]


class IndexMiddlePinchPlugin:
    """Detector-only plugin."""
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(
            detectors=[IndexMiddlePinchDetector()],
            actions={}
        )


def plugin():
    return IndexMiddlePinchPlugin()