# src/aircontrol/plugins/detectors/fist.py

from __future__ import annotations

import math
from typing import Optional, Tuple

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    THUMB_MCP,
    INDEX_TIP,
    INDEX_MCP,
    MIDDLE_TIP,
    MIDDLE_MCP,
    RING_TIP,
    RING_MCP,
    PINKY_TIP,
    PINKY_MCP,
    PALM_POINTS,
)


class FistDetector:
    """
    Closed fist detector (all four fingers folded; thumb folded required).
    Emits: gesture.fist
    """

    def __init__(
        self,
        hold_frames: int = 2,
        cooldown_frames: int = 2,
        move_tol: float = 0.10,
        min_detect_frames: int = 2,
        require_thumb_folded: bool = True,
        folded_margin: float = 0.03,
        thumb_fold_x_tol: float = 0.04,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.move_tol = float(move_tol)
        self.min_detect_frames = int(min_detect_frames)
        self.require_thumb_folded = bool(require_thumb_folded)
        self.folded_margin = float(folded_margin)
        self.thumb_fold_x_tol = float(thumb_fold_x_tol)

        self._hold_counter = 0
        self._cooldown = 0
        self._last_ref: Optional[Tuple[float, float]] = None
        self._detect_streak = 0
        self._armed = True  # release-to-rearm

    def _palm_center(self, lms) -> Tuple[float, float]:
        xs = [lms[i].x for i in PALM_POINTS]
        ys = [lms[i].y for i in PALM_POINTS]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _finger_folded(self, lms, tip: int, mcp: int) -> bool:
        return lms[tip].y >= lms[mcp].y + self.folded_margin

    def _thumb_folded(self, lms) -> bool:
        return abs(lms[THUMB_TIP].x - lms[THUMB_MCP].x) < self.thumb_fold_x_tol

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._hold_counter = 0
            self._detect_streak = 0
            self._last_ref = None
            self._armed = True
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        idx_fold = self._finger_folded(lms, INDEX_TIP, INDEX_MCP)
        mid_fold = self._finger_folded(lms, MIDDLE_TIP, MIDDLE_MCP)
        rng_fold = self._finger_folded(lms, RING_TIP, RING_MCP)
        pky_fold = self._finger_folded(lms, PINKY_TIP, PINKY_MCP)

        all_folded = idx_fold and mid_fold and rng_fold and pky_fold
        thumb_ok = (not self.require_thumb_folded) or self._thumb_folded(lms)

        gesture = all_folded and thumb_ok

        if not gesture:
            self._armed = True
            self._hold_counter = 0
            self._detect_streak = 0
            self._last_ref = None
            return []

        if not self._armed:
            return []

        self._detect_streak += 1
        if self._detect_streak < self.min_detect_frames:
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
            self._detect_streak = 0
            return [GestureEvent("gesture.fist", {})]

        return []


class FistPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[FistDetector()], actions={})


def plugin():
    return FistPlugin()