# src/aircontrol/plugins/detectors/open_palm.py

from __future__ import annotations

import math
from typing import Optional, Tuple

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    THUMB_IP,
    INDEX_TIP,
    INDEX_PIP,
    MIDDLE_TIP,
    MIDDLE_PIP,
    RING_TIP,
    RING_PIP,
    PINKY_TIP,
    PINKY_PIP,
    PALM_POINTS,
)


class OpenPalmHoldDetector:
    """
    Open palm hold detector (all fingers extended + thumb extended), held steady.
    Emits: gesture.open_palm_hold
    """

    def __init__(
        self,
        hold_frames: int = 3,
        cooldown_frames: int = 4,
        move_tol: float = 0.10,
        min_open_frames: int = 2,
        thumb_x_threshold: float = 0.03,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.move_tol = float(move_tol)
        self.min_open_frames = int(min_open_frames)
        self.thumb_x_threshold = float(thumb_x_threshold)

        self._hold_counter = 0
        self._cooldown = 0
        self._last_ref: Optional[Tuple[float, float]] = None
        self._open_streak = 0
        self._armed = True

    def _is_extended(self, lms, tip: int, pip: int) -> bool:
        return lms[tip].y < lms[pip].y

    def _thumb_extended(self, lms) -> bool:
        # simple-ish: thumb tip sufficiently far from thumb IP in x
        return abs(lms[THUMB_TIP].x - lms[THUMB_IP].x) > self.thumb_x_threshold

    def _palm_center(self, lms) -> Tuple[float, float]:
        xs = [lms[i].x for i in PALM_POINTS]
        ys = [lms[i].y for i in PALM_POINTS]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._hold_counter = 0
            self._open_streak = 0
            self._last_ref = None
            self._armed = True
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        index_ext = self._is_extended(lms, INDEX_TIP, INDEX_PIP)
        middle_ext = self._is_extended(lms, MIDDLE_TIP, MIDDLE_PIP)
        ring_ext = self._is_extended(lms, RING_TIP, RING_PIP)
        pinky_ext = self._is_extended(lms, PINKY_TIP, PINKY_PIP)
        thumb_ext = self._thumb_extended(lms)

        open_palm = index_ext and middle_ext and ring_ext and pinky_ext and thumb_ext

        if not open_palm:
            self._armed = True
            self._hold_counter = 0
            self._open_streak = 0
            self._last_ref = None
            return []

        if not self._armed:
            return []

        self._open_streak += 1
        if self._open_streak < self.min_open_frames:
            return []

        ref = self._palm_center(lms)

        if self._last_ref is not None:
            dx = ref[0] - self._last_ref[0]
            dy = ref[1] - self._last_ref[1]
            movement = math.hypot(dx, dy)

            if movement > self.move_tol:
                self._hold_counter = 0
                self._last_ref = ref
                return []

        self._last_ref = ref
        self._hold_counter += 1

        if self._hold_counter >= self.hold_frames:
            self._cooldown = self.cooldown_frames
            self._armed = False
            self._hold_counter = 0
            self._open_streak = 0
            return [GestureEvent("gesture.open_palm_hold", {})]

        return []


class OpenPalmHoldPlugin:
    """Detector-only plugin."""
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[OpenPalmHoldDetector()], actions={})


def plugin():
    return OpenPalmHoldPlugin()