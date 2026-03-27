# plugins/detectors/open_palm_pinky_folded.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class OpenPalmPinkyFoldedDetector:
    INDEX_TIP, INDEX_PIP = 8, 6
    MIDDLE_TIP, MIDDLE_PIP = 12, 10
    RING_TIP, RING_PIP = 16, 14
    PINKY_TIP, PINKY_PIP = 20, 18

    def __init__(self, hold_frames: int = 5, cooldown_frames: int = 20):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self._streak = 0
        self._cooldown = 0

    def _extended(self, lms, tip: int, pip: int) -> bool:
        return lms[tip].y < lms[pip].y

    def _folded(self, lms, tip: int, pip: int) -> bool:
        return lms[tip].y > lms[pip].y

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._streak = 0
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        index_up = self._extended(lms, self.INDEX_TIP, self.INDEX_PIP)
        middle_up = self._extended(lms, self.MIDDLE_TIP, self.MIDDLE_PIP)
        ring_up = self._extended(lms, self.RING_TIP, self.RING_PIP)
        pinky_down = self._folded(lms, self.PINKY_TIP, self.PINKY_PIP)

        gesture = index_up and middle_up and ring_up and pinky_down

        if gesture:
            self._streak += 1
        else:
            self._streak = 0
            return []

        if self._streak < self.hold_frames:
            return []

        self._streak = 0
        self._cooldown = self.cooldown_frames

        return [GestureEvent("gesture.open_palm_pinky_folded", {})]


class OpenPalmPinkyFoldedPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        return PluginRegistration(detectors=[OpenPalmPinkyFoldedDetector()], actions={})


def plugin():
    return OpenPalmPinkyFoldedPlugin()