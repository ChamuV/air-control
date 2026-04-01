# src/aircontrol/plugins/detectors/two_finger_hold.py

from __future__ import annotations

from typing import Optional

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP, THUMB_IP,
    INDEX_TIP, INDEX_PIP, INDEX_MCP,
    MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP,
    RING_TIP, RING_MCP,
    PINKY_TIP, PINKY_MCP,
)


class TwoFingerHoldDetector:
    """
    Two-Finger Hold (continuous scroll):

    Base pose (must hold):
      - thumb sideways
      - ring + pinky folded

    Mode selection (confirmed for mode_confirm_frames):
      - if index+middle are FULLY extended -> direction = "up"
      - if index+middle are PARTIALLY extended -> direction = "down"

    Control:
      - vertical motion of index+middle tips drives scroll amount

    Emits: gesture.two_finger_hold  with payload {"direction": "...", "amount": int}
    """

    def __init__(
        self,
        pose_confirm_frames: int = 2,
        mode_confirm_frames: int = 2,
        move_deadzone: float = 0.015,
        scroll_gain: float = 120.0,
        full_ext_thresh: float = 0.75,
        partial_ext_lo: float = 0.35,
        partial_ext_hi: float = 0.65,
    ):
        self.pose_confirm_frames = int(pose_confirm_frames)
        self.mode_confirm_frames = int(mode_confirm_frames)
        self.move_deadzone = float(move_deadzone)
        self.scroll_gain = float(scroll_gain)

        self.full_ext_thresh = float(full_ext_thresh)
        self.partial_ext_lo = float(partial_ext_lo)
        self.partial_ext_hi = float(partial_ext_hi)

        self._pose_streak = 0
        self._mode_streak = 0
        self._mode: Optional[str] = None  # "up" | "down"
        self._baseline_y: Optional[float] = None

    def _is_folded(self, lms, tip: int, mcp: int) -> bool:
        return lms[tip].y >= lms[mcp].y

    def _thumb_sideways(self, lms) -> bool:
        return abs(lms[THUMB_TIP].x - lms[THUMB_IP].x) > 0.04

    def _ext_score(self, lms, tip: int, pip: int, mcp: int) -> float:
        # same scoring as your original: higher = more extended
        a = (lms[pip].y - lms[tip].y)
        b = (lms[mcp].y - lms[tip].y)
        s = 0.6 * a + 0.4 * b
        return max(0.0, min(1.0, s * 2.5))

    def _reset(self) -> None:
        self._pose_streak = 0
        self._mode_streak = 0
        self._mode = None
        self._baseline_y = None

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._reset()
            return []

        lms = hand_landmarks.landmark

        # ---- base hold pose gate ----
        ring_fold = self._is_folded(lms, RING_TIP, RING_MCP)
        pinky_fold = self._is_folded(lms, PINKY_TIP, PINKY_MCP)
        thumb_ok = self._thumb_sideways(lms)

        if ring_fold and pinky_fold and thumb_ok:
            self._pose_streak += 1
        else:
            self._reset()
            return []

        if self._pose_streak < self.pose_confirm_frames:
            return []

        # ---- mode selection by extension level ----
        idx_s = self._ext_score(lms, INDEX_TIP, INDEX_PIP, INDEX_MCP)
        mid_s = self._ext_score(lms, MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP)
        ext = 0.5 * (idx_s + mid_s)

        desired_mode: Optional[str] = None
        if ext >= self.full_ext_thresh:
            desired_mode = "up"
        elif self.partial_ext_lo <= ext <= self.partial_ext_hi:
            desired_mode = "down"
        else:
            # in-between / unclear: don't emit, and don't accumulate movement
            self._mode_streak = 0
            self._baseline_y = None
            return []

        if desired_mode != self._mode:
            self._mode = desired_mode
            self._mode_streak = 1
            self._baseline_y = None
            return []

        self._mode_streak += 1
        if self._mode_streak < self.mode_confirm_frames:
            return []

        # ---- movement drives scroll ----
        y_pos = 0.5 * (lms[INDEX_TIP].y + lms[MIDDLE_TIP].y)

        if self._baseline_y is None:
            self._baseline_y = y_pos
            return []

        dy = y_pos - self._baseline_y

        if abs(dy) < self.move_deadzone:
            return []

        amount = int(abs(dy) * self.scroll_gain)
        if amount == 0:
            return []

        # Advance baseline after each emitted step so held position
        # does not repeatedly re-emit the same scroll amount.
        self._baseline_y = y_pos

        # IMPORTANT: scrolling direction uses mode,
        # not dy sign (you wanted "if fully extended -> go up" etc.)
        return [
            GestureEvent(
                "gesture.two_finger_hold",
                {"direction": self._mode, "amount": amount},
            )
        ]


class TwoFingerHoldPlugin:
    """Detector-only plugin."""
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[TwoFingerHoldDetector()], actions={})


def plugin():
    return TwoFingerHoldPlugin()
