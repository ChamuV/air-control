# src/aircontrol/plugins/detectors/middle_pinch.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    MIDDLE_TIP,
    INDEX_TIP,
    RING_TIP,
    PINKY_TIP,
    dist,
)


class MiddlePinchDetector:
    """
    Thumb–Middle pinch => gesture.middle_pinch

    Extra "nothing else" check:
      - index/ring/pinky tips should NOT be close to thumb tip
        (prevents accidental trigger when you do a multi-finger pinch)
    """

    def __init__(
        self,
        pinch_threshold: float = 0.04,
        other_finger_min_dist: float = 0.06,
        cooldown_frames: int = 8,
    ):
        self.pinch_threshold = float(pinch_threshold)
        self.other_finger_min_dist = float(other_finger_min_dist)
        self.cooldown_frames = int(cooldown_frames)
        self._cooldown = 0

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        d_tm = dist(lms, THUMB_TIP, MIDDLE_TIP)

        # "nothing else": other tips shouldn't also be near thumb
        d_ti = dist(lms, THUMB_TIP, INDEX_TIP)
        d_tr = dist(lms, THUMB_TIP, RING_TIP)
        d_tp = dist(lms, THUMB_TIP, PINKY_TIP)

        gesture = (
            d_tm < self.pinch_threshold
            and d_ti > self.other_finger_min_dist
            and d_tr > self.other_finger_min_dist
            and d_tp > self.other_finger_min_dist
        )

        if not gesture:
            return []

        self._cooldown = self.cooldown_frames
        return [GestureEvent("gesture.middle_pinch", {"d_tm": d_tm})]


class MiddlePinchPlugin:
    """Detector-only plugin."""
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[MiddlePinchDetector()], actions={})


def plugin():
    return MiddlePinchPlugin()