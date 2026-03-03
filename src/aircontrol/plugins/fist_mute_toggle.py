# src/aircontrol/plugins/fist_mute_toggle.py

# src/aircontrol/plugins/fist_mute_toggle.py

from __future__ import annotations

import math
from typing import Optional, Tuple

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class FistMuteToggleDetector:
    # Finger tips + MCPs 
    INDEX_TIP, INDEX_MCP = 8, 5
    MIDDLE_TIP, MIDDLE_MCP = 12, 9
    RING_TIP, RING_MCP = 16, 13
    PINKY_TIP, PINKY_MCP = 20, 17

    # Thumb 
    THUMB_TIP, THUMB_MCP = 4, 2

    PALM_IDS = (0, 5, 9, 13, 17)

    def __init__(
        self,
        hold_frames: int = 2,
        cooldown_frames: int = 2,
        move_tol: float = 0.10,
        min_detect_frames: int = 2,
        require_thumb_folded: bool = False,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.move_tol = float(move_tol)
        self.min_detect_frames = int(min_detect_frames)
        self.require_thumb_folded = bool(require_thumb_folded)

        self._hold_counter = 0
        self._cooldown = 0
        self._last_ref: Optional[Tuple[float, float]] = None
        self._detect_streak = 0

        # release-to-rearm
        self._armed = True

    def _palm_center(self, lms) -> Tuple[float, float]:
        xs = [lms[i].x for i in self.PALM_IDS]
        ys = [lms[i].y for i in self.PALM_IDS]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _finger_folded(self, lms, tip: int, mcp: int) -> bool:
        # folded-ish if tip is not above MCP
        return lms[tip].y >= lms[mcp].y

    def _thumb_folded(self, lms) -> bool:
        # simple-ish: tip not far from MCP in x, and not clearly extended
        return abs(lms[self.THUMB_TIP].x - lms[self.THUMB_MCP].x) < 0.04

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

        all_folded = idx_fold and mid_fold and rng_fold and pky_fold
        thumb_ok = (not self.require_thumb_folded) or self._thumb_folded(lms)

        gesture = all_folded and thumb_ok

        # --- DEBUG (single-line comments so you can toggle later) ---
        # print(
        #     f"[FIST DEBUG] folded(I,M,R,P)=({idx_fold},{mid_fold},{rng_fold},{pky_fold}) "
        #     f"thumb_ok={thumb_ok} GESTURE={gesture} ARMED={self._armed} "
        #     f"streak={self._detect_streak}/{self.min_detect_frames} "
        #     f"hold={self._hold_counter}/{self.hold_frames}"
        # )
        # -----------------------------------------------------------

        if not gesture:
            # release -> rearm
            # if self._armed is False:
            #     print("[FIST] released -> re-armed")
            self._armed = True
            self._hold_counter = 0
            self._detect_streak = 0
            self._last_ref = None
            return []

        if not self._armed:
            # print("[FIST] gesture but NOT armed (waiting for release)")
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
                # print(f"[FIST] movement reset: {movement:.4f} > {self.move_tol}")
                self._hold_counter = 0
                self._last_ref = ref
                return []

        self._last_ref = ref
        self._hold_counter += 1

        # print(f"[FIST] holding... {self._hold_counter}/{self.hold_frames}")

        if self._hold_counter >= self.hold_frames:
            # print("[FIST] FIRING media.mute_toggle")
            self._cooldown = self.cooldown_frames
            self._armed = False
            self._hold_counter = 0
            self._detect_streak = 0
            return [GestureEvent("media.mute_toggle", {})]

        return []


class FistMuteTogglePlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = FistMuteToggleDetector()

        def mute_action(event: GestureEvent) -> None:
            ctx.media.toggle_mute()

        return PluginRegistration(
            detectors=[detector],
            actions={"media.mute_toggle": mute_action},
        )


def plugin():
    return FistMuteTogglePlugin()