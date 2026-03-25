# plugins/detectors/flag_wave.py

from __future__ import annotations

from collections import deque
from typing import Deque, Optional, Tuple

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
)


class FlagWaveDetector:
    """
    Flag pose:
      - thumb up
      - fingers open sideways
      - fingertips roughly aligned in x

    After the pose is held briefly, detect a quick horizontal swipe
    of the fingertips cluster:

      - quick motion to the right -> gesture.flag_wave_right
      - quick motion to the left  -> gesture.flag_wave_left
    """

    def __init__(
        self,
        hold_frames: int = 1,
        cooldown_frames: int = 6,
        tip_x_spread_max: float = 0.10,
        thumb_up_margin: float = 0.035,
        finger_open_x_margin: float = 0.035,
        history_len: int = 2,
        swipe_dx_threshold: float = 0.040,
        instant_dx_threshold: float = 0.012,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.tip_x_spread_max = float(tip_x_spread_max)
        self.thumb_up_margin = float(thumb_up_margin)
        self.finger_open_x_margin = float(finger_open_x_margin)

        self.history_len = int(history_len)
        self.swipe_dx_threshold = float(swipe_dx_threshold)
        self.instant_dx_threshold = float(instant_dx_threshold)

        self._hold_counter = 0
        self._cooldown = 0
        self._armed = False
        self._x_history: Deque[float] = deque(maxlen=self.history_len)

    def _reset(self) -> None:
        self._hold_counter = 0
        self._armed = False
        self._x_history.clear()

    def _avg_tip_x(self, lms) -> float:
        tips = [lms[INDEX_TIP], lms[MIDDLE_TIP], lms[RING_TIP], lms[PINKY_TIP]]
        return sum(p.x for p in tips) / 4.0

    def _tip_x_spread(self, lms) -> float:
        xs = [lms[INDEX_TIP].x, lms[MIDDLE_TIP].x, lms[RING_TIP].x, lms[PINKY_TIP].x]
        return max(xs) - min(xs)

    def _thumb_up(self, lms) -> bool:
        return lms[THUMB_TIP].y < lms[THUMB_MCP].y - self.thumb_up_margin

    def _fingers_open_horizontal(self, lms) -> bool:
        tip_spread_ok = self._tip_x_spread(lms) <= self.tip_x_spread_max

        avg_tip_x = self._avg_tip_x(lms)
        avg_mcp_x = (
            lms[INDEX_MCP].x
            + lms[MIDDLE_MCP].x
            + lms[RING_MCP].x
            + lms[PINKY_MCP].x
        ) / 4.0

        fingers_extended_sideways = abs(avg_tip_x - avg_mcp_x) >= self.finger_open_x_margin
        return tip_spread_ok and fingers_extended_sideways

    def _is_flag_pose(self, lms) -> bool:
        return self._thumb_up(lms) and self._fingers_open_horizontal(lms)

    def _detect_swipe(self) -> Optional[str]:
        if len(self._x_history) < 3:
            return None

        xs = list(self._x_history)

        total_dx = xs[-1] - xs[0]
        last_dx = xs[-1] - xs[-2]

        # Require both:
        # 1. enough total movement across recent frames
        # 2. recent step is still moving in that direction
        if total_dx >= self.swipe_dx_threshold and last_dx >= self.instant_dx_threshold:
            return "right"

        if total_dx <= -self.swipe_dx_threshold and last_dx <= -self.instant_dx_threshold:
            return "left"

        return None

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._reset()
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        if not self._is_flag_pose(lms):
            self._reset()
            return []

        current_tip_x = self._avg_tip_x(lms)

        # Arm only after briefly holding the pose
        if not self._armed:
            self._hold_counter += 1
            self._x_history.clear()
            self._x_history.append(current_tip_x)

            if self._hold_counter >= self.hold_frames:
                self._armed = True

            return []

        # Once armed, track recent fingertip x positions
        self._x_history.append(current_tip_x)

        direction = self._detect_swipe()
        if direction == "right":
            self._cooldown = self.cooldown_frames
            self._hold_counter = 0
            self._armed = False
            self._x_history.clear()
            return [GestureEvent("gesture.flag_wave_right", {})]

        if direction == "left":
            self._cooldown = self.cooldown_frames
            self._hold_counter = 0
            self._armed = False
            self._x_history.clear()
            return [GestureEvent("gesture.flag_wave_left", {})]

        return []


class FlagWavePlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[FlagWaveDetector()], actions={})


def plugin():
    return FlagWavePlugin()