# src/aircontrol/plugins/detectors/thumbs_up.py

from __future__ import annotations

import math
from typing import Optional, Tuple

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    WRIST,
    THUMB_TIP,
    THUMB_MCP,
    THUMB_IP,
    INDEX_TIP,
    INDEX_MCP,
    MIDDLE_TIP,
    MIDDLE_MCP,
    RING_TIP,
    RING_MCP,
    PINKY_TIP,
    PINKY_MCP,
    PALM_POINTS,
    dist,
)


class ThumbsUpHoldDetector:
    """
    Continuous hold detector for gesture.volume_up_hold.
    Emits repeatedly while a stable thumbs-up pose is held.
    """

    def __init__(
        self,
        hold_frames: int = 2,
        repeat_every_frames: int = 3,
        move_tol: float = 0.12,
        min_detect_frames: int = 1,
        thumb_up_y_margin: float = 0.03,
        thumb_side_limit: float = 0.18,
        thumb_extend_margin: float = 0.015,
        folded_margin: float = 0.02,
        min_folded_fingers: int = 2,
    ):
        self.hold_frames = int(hold_frames)
        self.repeat_every_frames = int(repeat_every_frames)
        self.move_tol = float(move_tol)
        self.min_detect_frames = int(min_detect_frames)

        self.thumb_up_y_margin = float(thumb_up_y_margin)
        self.thumb_side_limit = float(thumb_side_limit)
        self.thumb_extend_margin = float(thumb_extend_margin)
        self.folded_margin = float(folded_margin)
        self.min_folded_fingers = int(min_folded_fingers)

        self._hold_counter = 0
        self._detect_streak = 0
        self._last_ref: Optional[Tuple[float, float]] = None

    def _palm_center(self, lms) -> Tuple[float, float]:
        xs = [lms[i].x for i in PALM_POINTS]
        ys = [lms[i].y for i in PALM_POINTS]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _finger_folded(self, lms, tip: int, mcp: int) -> bool:
        return lms[tip].y >= lms[mcp].y + self.folded_margin

    def _count_non_thumb_fingers_folded(self, lms) -> int:
        return sum([
            self._finger_folded(lms, INDEX_TIP, INDEX_MCP),
            self._finger_folded(lms, MIDDLE_TIP, MIDDLE_MCP),
            self._finger_folded(lms, RING_TIP, RING_MCP),
            self._finger_folded(lms, PINKY_TIP, PINKY_MCP),
        ])

    def _thumb_extended(self, lms) -> bool:
        return dist(lms, THUMB_TIP, WRIST) > dist(lms, THUMB_MCP, WRIST) + self.thumb_extend_margin

    def _is_thumbs_up(self, lms) -> bool:
        folded_count = self._count_non_thumb_fingers_folded(lms)
        if folded_count < self.min_folded_fingers:
            return False

        if not self._thumb_extended(lms):
            return False

        thumb_tip = lms[THUMB_TIP]
        thumb_mcp = lms[THUMB_MCP]
        thumb_ip = lms[THUMB_IP]

        thumb_is_up = (
            thumb_tip.y < thumb_mcp.y - self.thumb_up_y_margin
            and thumb_tip.y < thumb_ip.y
        )

        not_too_sideways = abs(thumb_tip.x - thumb_mcp.x) < self.thumb_side_limit
        return thumb_is_up and not_too_sideways

    def _reset(self) -> None:
        self._hold_counter = 0
        self._detect_streak = 0
        self._last_ref = None

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._reset()
            return []

        lms = hand_landmarks.landmark

        if not self._is_thumbs_up(lms):
            self._reset()
            return []

        ref = self._palm_center(lms)

        if self._last_ref is not None:
            dx = ref[0] - self._last_ref[0]
            dy = ref[1] - self._last_ref[1]
            movement = math.hypot(dx, dy)
            if movement > self.move_tol:
                self._hold_counter = 0
                self._detect_streak = 0
                self._last_ref = ref
                return []

        self._last_ref = ref
        self._detect_streak += 1

        if self._detect_streak < self.min_detect_frames:
            return []

        self._hold_counter += 1

        if self._hold_counter >= self.hold_frames:
            offset = self._hold_counter - self.hold_frames
            if offset % self.repeat_every_frames == 0:
                return [GestureEvent("gesture.volume_up_hold", {})]

        return []


class ThumbsUpHoldPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[ThumbsUpHoldDetector()], actions={})


def plugin():
    return ThumbsUpHoldPlugin()