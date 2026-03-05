# src/aircontrol/plugins/detectors/call_sign.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    THUMB_IP,
    INDEX_MCP,
    INDEX_TIP,
    INDEX_PIP,
    MIDDLE_TIP,
    MIDDLE_PIP,
    RING_TIP,
    RING_PIP,
    PINKY_TIP,
    PINKY_MCP,
)


class CallSignDetector:
    """
    "Call me" gesture:

      - Thumb up + sideways
      - Pinky sideways
      - Index/Middle/Ring folded

    Emits: gesture.call_sign
    """

    def __init__(
        self,
        hold_frames: int = 8,
        cooldown_frames: int = 30,
        pinky_side_x_thresh: float = 0.055,
        thumb_side_x_thresh: float = 0.040,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)

        self._hold_counter = 0
        self._cooldown = 0

        self.pinky_side_x_thresh = float(pinky_side_x_thresh)
        self.thumb_side_x_thresh = float(thumb_side_x_thresh)

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._hold_counter = 0
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        thumb_up = lms[THUMB_TIP].y < lms[THUMB_IP].y
        thumb_side = abs(lms[THUMB_TIP].x - lms[INDEX_MCP].x) > self.thumb_side_x_thresh

        pinky_side = abs(lms[PINKY_TIP].x - lms[PINKY_MCP].x) > self.pinky_side_x_thresh

        index_folded = lms[INDEX_TIP].y > lms[INDEX_PIP].y
        middle_folded = lms[MIDDLE_TIP].y > lms[MIDDLE_PIP].y
        ring_folded = lms[RING_TIP].y > lms[RING_PIP].y

        gesture = (
            thumb_up
            and thumb_side
            and pinky_side
            and index_folded
            and middle_folded
            and ring_folded
        )

        if gesture:
            self._hold_counter += 1

            if self._hold_counter >= self.hold_frames:
                self._hold_counter = 0
                self._cooldown = self.cooldown_frames
                return [GestureEvent("gesture.call_sign", {})]

        else:
            self._hold_counter = 0

        return []


class CallSignPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[CallSignDetector()], actions={})


def plugin():
    return CallSignPlugin()