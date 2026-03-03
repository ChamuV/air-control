# src/aircontrol/plugins/facetime_me.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.actions.facetime_control import FaceTimeControllerMacOS


class CallMeDetector:
    """
    "Call me" gesture:
      - Thumb up
      - Pinky out sideways
      - Index/Middle/Ring folded

    Requires:
      - Gesture held for hold_frames consecutive frames
      - Cooldown after trigger
    """

    THUMB_TIP = 4
    THUMB_IP = 3
    INDEX_MCP = 5

    INDEX_TIP = 8
    INDEX_PIP = 6

    MIDDLE_TIP = 12
    MIDDLE_PIP = 10

    RING_TIP = 16
    RING_PIP = 14

    PINKY_TIP = 20
    PINKY_MCP = 17

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

        # Thumb up
        thumb_up = lms[self.THUMB_TIP].y < lms[self.THUMB_IP].y

        # Thumb sideways
        thumb_side = abs(lms[self.THUMB_TIP].x - lms[self.INDEX_MCP].x) > self.thumb_side_x_thresh

        # Pinky sideways
        pinky_side = abs(lms[self.PINKY_TIP].x - lms[self.PINKY_MCP].x) > self.pinky_side_x_thresh

        # Other fingers folded
        index_folded = lms[self.INDEX_TIP].y > lms[self.INDEX_PIP].y
        middle_folded = lms[self.MIDDLE_TIP].y > lms[self.MIDDLE_PIP].y
        ring_folded = lms[self.RING_TIP].y > lms[self.RING_PIP].y

        is_call_me = (
            thumb_up
            and thumb_side
            and pinky_side
            and index_folded
            and middle_folded
            and ring_folded
        )

        if is_call_me:
            self._hold_counter += 1

            if self._hold_counter >= self.hold_frames:
                self._hold_counter = 0
                self._cooldown = self.cooldown_frames
                return [GestureEvent("facetime.call", {})]
        else:
            self._hold_counter = 0

        return []


class CallMePlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = CallMeDetector()

        # HARD-CODE NUMBER HERE (E.164)
        facetime = FaceTimeControllerMacOS("+919845103831")

        def call_action(event: GestureEvent) -> None:
            facetime.call()

        return PluginRegistration(
            detectors=[detector],
            actions={"facetime.call": call_action},
        )


def plugin():
    return CallMePlugin()