# src/aircontrol/plugins/thumbs_down_quit.py

from __future__ import annotations

import math
import sys
from typing import Optional, Tuple

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class ThumbsDownQuitDetector:
    # Fingers
    INDEX_TIP, INDEX_MCP = 8, 5
    MIDDLE_TIP, MIDDLE_MCP = 12, 9
    RING_TIP, RING_MCP = 16, 13
    PINKY_TIP, PINKY_MCP = 20, 17

    # Thumb
    THUMB_TIP, THUMB_MCP = 4, 2
    WRIST = 0

    PALM_IDS = (0, 5, 9, 13, 17)

    def __init__(
        self,
        hold_frames: int = 2,
        cooldown_frames: int = 4,
        move_tol: float = 0.10,
        min_detect_frames: int = 2,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.move_tol = float(move_tol)
        self.min_detect_frames = int(min_detect_frames)

        self._hold_counter = 0
        self._cooldown = 0
        self._last_ref: Optional[Tuple[float, float]] = None
        self._detect_streak = 0
        self._armed = True

    def _palm_center(self, lms) -> Tuple[float, float]:
        xs = [lms[i].x for i in self.PALM_IDS]
        ys = [lms[i].y for i in self.PALM_IDS]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _finger_folded(self, lms, tip: int, mcp: int) -> bool:
        return lms[tip].y >= lms[mcp].y

    def _thumb_down(self, lms) -> bool:
        return (
            lms[self.THUMB_TIP].y > lms[self.WRIST].y
            and lms[self.THUMB_TIP].y > lms[self.THUMB_MCP].y
        )

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

        idx_fold = self._finger_folded(lms, self.INDEX_TIP, self.INDEX_MCP)
        mid_fold = self._finger_folded(lms, self.MIDDLE_TIP, self.MIDDLE_MCP)
        rng_fold = self._finger_folded(lms, self.RING_TIP, self.RING_MCP)
        pky_fold = self._finger_folded(lms, self.PINKY_TIP, self.PINKY_MCP)

        thumb_down = self._thumb_down(lms)

        gesture = thumb_down and idx_fold and mid_fold and rng_fold and pky_fold

        # print(
        #     f"[TD DEBUG] thumb_down={thumb_down} "
        #     f"fold(I,M,R,P)=({idx_fold},{mid_fold},{rng_fold},{pky_fold}) "
        #     f"GESTURE={gesture} ARMED={self._armed} "
        #     f"streak={self._detect_streak}/{self.min_detect_frames} "
        #     f"hold={self._hold_counter}/{self.hold_frames}"
        # )

        if not gesture:
            # if self._armed is False:
            #     print("[TD] released -> re-armed")

            self._armed = True
            self._hold_counter = 0
            self._detect_streak = 0
            self._last_ref = None
            return []

        if not self._armed:
            # print("[TD] gesture but NOT armed (waiting for release)")
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
                # print(f"[TD] movement reset: {movement:.4f} > {self.move_tol}")
                self._hold_counter = 0
                self._last_ref = ref
                return []

        self._last_ref = ref
        self._hold_counter += 1

        if self._hold_counter >= self.hold_frames:
            # print("[TD] FIRING app.quit")

            self._cooldown = self.cooldown_frames
            self._armed = False
            self._hold_counter = 0
            self._detect_streak = 0
            return [GestureEvent("app.quit", {})]

        return []


class ThumbsDownQuitPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = ThumbsDownQuitDetector()

        def quit_action(event: GestureEvent) -> None:
            print("Quitting AirControl...")
            sys.exit(0)

        return PluginRegistration(
            detectors=[detector],
            actions={"app.quit": quit_action},
        )


def plugin():
    return ThumbsDownQuitPlugin()