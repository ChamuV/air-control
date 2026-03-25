# plugins/detectors/vulcan.py

from __future__ import annotations

import math
from typing import Optional, Tuple

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    INDEX_TIP,
    INDEX_MCP,
    MIDDLE_TIP,
    MIDDLE_MCP,
    RING_TIP,
    RING_MCP,
    PINKY_TIP,
    PINKY_MCP,
    INDEX_TIP,
    MIDDLE_TIP,
    RING_TIP,
    PINKY_TIP,
    PALM_POINTS,
    dist,
)


class VulcanSaluteDetector:
    """
    Vulcan salute detector:
    - index + middle extended
    - ring + pinky extended
    - gap between middle and ring is noticeably larger
    Emits: gesture.vulcan_salute
    """

    def __init__(
        self,
        hold_frames: int = 4,
        cooldown_frames: int = 4,
        move_tol: float = 0.10,
        min_detect_frames: int = 2,
        split_ratio: float = 1.6,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.move_tol = float(move_tol)
        self.min_detect_frames = int(min_detect_frames)
        self.split_ratio = float(split_ratio)

        self._hold_counter = 0
        self._cooldown = 0
        self._last_ref: Optional[Tuple[float, float]] = None
        self._detect_streak = 0
        self._armed = True

    def _palm_center(self, lms) -> Tuple[float, float]:
        xs = [lms[i].x for i in PALM_POINTS]
        ys = [lms[i].y for i in PALM_POINTS]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _finger_extended(self, lms, tip: int, mcp: int) -> bool:
        return lms[tip].y < lms[mcp].y

    def _is_vulcan(self, lms) -> bool:
        idx_up = self._finger_extended(lms, INDEX_TIP, INDEX_MCP)
        mid_up = self._finger_extended(lms, MIDDLE_TIP, MIDDLE_MCP)
        rng_up = self._finger_extended(lms, RING_TIP, RING_MCP)
        pky_up = self._finger_extended(lms, PINKY_TIP, PINKY_MCP)

        if not (idx_up and mid_up and rng_up and pky_up):
            return False

        gap_im = dist(lms, INDEX_TIP, MIDDLE_TIP)
        gap_mr = dist(lms, MIDDLE_TIP, RING_TIP)
        gap_rp = dist(lms, RING_TIP, PINKY_TIP)

        avg_side_gap = (gap_im + gap_rp) / 2.0
        return gap_mr > self.split_ratio * avg_side_gap

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
        gesture = self._is_vulcan(lms)

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
            return [GestureEvent("gesture.vulcan_salute", {})]

        return []


class VulcanPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[VulcanSaluteDetector()], actions={})


def plugin():
    return VulcanPlugin()