from __future__ import annotations

import math
from typing import Optional

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class ContinuousTwoFingerScrollDetector:
    INDEX_TIP, INDEX_PIP, INDEX_MCP = 8, 6, 5
    MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP = 12, 10, 9
    RING_TIP, RING_MCP = 16, 13
    PINKY_TIP, PINKY_MCP = 20, 17
    THUMB_TIP, THUMB_IP = 4, 3

    def __init__(
        self,
        min_fold_frames: int = 2,
        neutral_deadzone: float = 0.03,
        scroll_gain: float = 120.0,   # MAIN tuning knob
    ):
        self.min_fold_frames = int(min_fold_frames)
        self.neutral_deadzone = float(neutral_deadzone)
        self.scroll_gain = float(scroll_gain)

        self._fold_streak = 0
        self._baseline: Optional[float] = None

    def _is_folded(self, lms, tip: int, mcp: int) -> bool:
        return lms[tip].y >= lms[mcp].y

    def _thumb_sideways(self, lms) -> bool:
        # thumb pointing outward sideways (x difference large)
        return abs(lms[self.THUMB_TIP].x - lms[self.THUMB_IP].x) > 0.04

    def _ext_score(self, lms, tip: int, pip: int, mcp: int) -> float:
        # higher when more extended
        a = (lms[pip].y - lms[tip].y)
        b = (lms[mcp].y - lms[tip].y)
        s = 0.6 * a + 0.4 * b
        return max(0.0, min(1.0, s * 2.5))

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._fold_streak = 0
            self._baseline = None
            return []

        lms = hand_landmarks.landmark

        ring_fold = self._is_folded(lms, self.RING_TIP, self.RING_MCP)
        pinky_fold = self._is_folded(lms, self.PINKY_TIP, self.PINKY_MCP)
        thumb_ok = self._thumb_sideways(lms)

        if ring_fold and pinky_fold and thumb_ok:
            self._fold_streak += 1
        else:
            # pose broken -> stop scrolling
            self._fold_streak = 0
            self._baseline = None
            return []

        if self._fold_streak < self.min_fold_frames:
            return []

        idx_s = self._ext_score(lms, self.INDEX_TIP, self.INDEX_PIP, self.INDEX_MCP)
        mid_s = self._ext_score(lms, self.MIDDLE_TIP, self.MIDDLE_PIP, self.MIDDLE_MCP)

        score = 0.5 * (idx_s + mid_s)

        if self._baseline is None:
            # set neutral position when entering pose
            self._baseline = score
            return []

        delta = score - self._baseline

        if abs(delta) < self.neutral_deadzone:
            return []

        # continuous scroll amount
        scroll_amount = int(delta * self.scroll_gain)

        if scroll_amount == 0:
            return []

        direction = "down" if scroll_amount > 0 else "up"

        return [
            GestureEvent(
                "scroll.continuous",
                {
                    "direction": direction,
                    "amount": abs(scroll_amount),
                },
            )
        ]


class ContinuousTwoFingerScrollPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = ContinuousTwoFingerScrollDetector()

        def scroll_action(event: GestureEvent) -> None:
            direction = event.payload.get("direction")
            amount = int(event.payload.get("amount", 1))

            if direction == "down":
                ctx.mouse.scroll(-amount)
            else:
                ctx.mouse.scroll(amount)

        return PluginRegistration(
            detectors=[detector],
            actions={"scroll.continuous": scroll_action},
        )


def plugin():
    return ContinuousTwoFingerScrollPlugin()