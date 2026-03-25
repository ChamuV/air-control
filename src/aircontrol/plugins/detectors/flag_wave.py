# plugins/dectectors/flag_wave.py

from __future__ import annotations

from typing import Optional

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

    Hold the pose briefly, then wave the fingertips cluster:
      - fingertips move right  -> gesture.window_wave_right
      - fingertips move left   -> gesture.window_wave_left
    """

    def __init__(
        self,
        hold_frames: int = 2,
        cooldown_frames: int = 6,
        tip_x_spread_max: float = 0.10,
        thumb_up_margin: float = 0.035,
        finger_open_x_margin: float = 0.035,
        wave_delta_x: float = 0.035,
        rebaseline_blend: float = 0.25,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.tip_x_spread_max = float(tip_x_spread_max)
        self.thumb_up_margin = float(thumb_up_margin)
        self.finger_open_x_margin = float(finger_open_x_margin)
        self.wave_delta_x = float(wave_delta_x)
        self.rebaseline_blend = float(rebaseline_blend)

        self._hold_counter = 0
        self._cooldown = 0
        self._armed = False
        self._baseline_tip_x: Optional[float] = None

    def _reset(self) -> None:
        self._hold_counter = 0
        self._armed = False
        self._baseline_tip_x = None

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

        if not self._armed:
            self._hold_counter += 1
            if self._hold_counter >= self.hold_frames:
                self._armed = True
                self._baseline_tip_x = current_tip_x
            return []

        if self._baseline_tip_x is None:
            self._baseline_tip_x = current_tip_x
            return []

        dx = current_tip_x - self._baseline_tip_x

        if dx >= self.wave_delta_x:
            self._cooldown = self.cooldown_frames
            self._reset()
            return [GestureEvent("gesture.flag_wave_right", {})]

        if dx <= -self.wave_delta_x:
            self._cooldown = self.cooldown_frames
            self._reset()
            return [GestureEvent("gesture.flag_wave_left", {})]

        # slowly adapt baseline while still holding pose
        self._baseline_tip_x = (
            (1.0 - self.rebaseline_blend) * self._baseline_tip_x
            + self.rebaseline_blend * current_tip_x
        )

        return []


class FlagWavePlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[FlagWaveDetector()], actions={})


def plugin():
    return FlagWavePlugin()