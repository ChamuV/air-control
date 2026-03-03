# src/aircontrol/plugins/hold_open_palm_play_pause.py

from __future__ import annotations

import math
from typing import Optional, Tuple

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class HoldOpenPalmDetector:
    INDEX_TIP, INDEX_PIP = 8, 6
    MIDDLE_TIP, MIDDLE_PIP = 12, 10
    RING_TIP, RING_PIP = 16, 14
    PINKY_TIP, PINKY_PIP = 20, 18

    THUMB_TIP, THUMB_IP = 4, 3

    PALM_IDS = (0, 5, 9, 13, 17)

    def __init__(
        self,
        hold_frames: int = 6,
        cooldown_frames: int = 45,
        move_tol: float = 0.10,
        min_open_frames: int = 2,
    ):
        self.hold_frames = hold_frames
        self.cooldown_frames = cooldown_frames
        self.move_tol = move_tol
        self.min_open_frames = min_open_frames

        self._hold_counter = 0
        self._cooldown = 0
        self._last_ref: Optional[Tuple[float, float]] = None
        self._open_streak = 0  # debounce counter

    def _is_extended(self, lms, tip: int, pip: int) -> bool:
        return lms[tip].y < lms[pip].y

    def _thumb_extended(self, lms) -> bool:
        return abs(lms[self.THUMB_TIP].x - lms[self.THUMB_IP].x) > 0.03

    def _palm_center(self, lms) -> Tuple[float, float]:
        xs = [lms[i].x for i in self.PALM_IDS]
        ys = [lms[i].y for i in self.PALM_IDS]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def update(self, hand_landmarks) -> list[GestureEvent]:

        if hand_landmarks is None:
            self._hold_counter = 0
            self._open_streak = 0
            self._last_ref = None
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        index_ext = self._is_extended(lms, self.INDEX_TIP, self.INDEX_PIP)
        middle_ext = self._is_extended(lms, self.MIDDLE_TIP, self.MIDDLE_PIP)
        ring_ext = self._is_extended(lms, self.RING_TIP, self.RING_PIP)
        pinky_ext = self._is_extended(lms, self.PINKY_TIP, self.PINKY_PIP)
        thumb_ext = self._thumb_extended(lms)

        open_palm = index_ext and middle_ext and ring_ext and pinky_ext and thumb_ext

        # ---------------- DEBUG ----------------
        print(
            f"[PALM DEBUG] "
            f"I:{index_ext} "
            f"M:{middle_ext} "
            f"R:{ring_ext} "
            f"P:{pinky_ext} "
            f"T:{thumb_ext} "
            f"OPEN:{open_palm}"
        )
        # ---------------------------------------

        if not open_palm:
            self._hold_counter = 0
            self._open_streak = 0
            self._last_ref = None
            return []

        # debounce: require open palm for a few frames first
        self._open_streak += 1

        print(f"[PALM] open_streak={self._open_streak}/{self.min_open_frames}")

        if self._open_streak < self.min_open_frames:
            return []

        ref = self._palm_center(lms)

        if self._last_ref is not None:
            dx = ref[0] - self._last_ref[0]
            dy = ref[1] - self._last_ref[1]
            movement = math.hypot(dx, dy)

            if movement > self.move_tol:
                print(f"[PALM] movement reset: {movement:.4f} > {self.move_tol}")
                self._hold_counter = 0
                self._last_ref = ref
                return []

        self._last_ref = ref
        self._hold_counter += 1

        print(f"[PALM] holding... {self._hold_counter}/{self.hold_frames}")

        if self._hold_counter >= self.hold_frames:
            print("[PALM] FIRING media.play_pause")
            self._cooldown = self.cooldown_frames
            self._hold_counter = 0
            self._open_streak = 0
            return [GestureEvent("media.play_pause", {})]

        return []
    """def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            # reset hold state, but keep cooldown (prevents re-trigger on brief tracking drop)
            self._hold_counter = 0
            self._last_ref = None
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        index_ext = self._is_extended(lms, self.INDEX_TIP, self.INDEX_PIP)
        middle_ext = self._is_extended(lms, self.MIDDLE_TIP, self.MIDDLE_PIP)
        ring_ext = self._is_extended(lms, self.RING_TIP, self.RING_PIP)
        pinky_ext = self._is_extended(lms, self.PINKY_TIP, self.PINKY_PIP)
        thumb_ext = self._thumb_extended(lms)

        open_palm = index_ext and middle_ext and ring_ext and pinky_ext and thumb_ext

        if not open_palm:
            self._hold_counter = 0
            self._last_ref = None
            return []

        ref = self._palm_center(lms)

        # steadiness check (restart hold if moving too much)
        if self._last_ref is not None:
            dx = ref[0] - self._last_ref[0]
            dy = ref[1] - self._last_ref[1]
            if math.hypot(dx, dy) > self.move_tol:
                self._hold_counter = 0
                self._last_ref = ref
                return []

        self._last_ref = ref
        self._hold_counter += 1

        if self._hold_counter >= self.hold_frames:
            self._cooldown = self.cooldown_frames
            self._hold_counter = 0
            return [GestureEvent("media.play_pause", {})]

        return []"""


class HoldOpenPalmPlayPausePlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = HoldOpenPalmDetector()

        def play_pause_action(event: GestureEvent) -> None:
            ctx.media.toggle_play_pause()

        return PluginRegistration(
            detectors=[detector],
            actions={"media.play_pause": play_pause_action},
        )


def plugin():
    return HoldOpenPalmPlayPausePlugin()