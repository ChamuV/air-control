# src/aircontrol/plugins/detectors/pinky_pinch.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.tracking.hand_landmarks import THUMB_TIP, PINKY_TIP, dist


class PinkyPinchDetector:
    def __init__(self, threshold: float = 0.045, release_multiplier: float = 1.2):
        self.threshold = float(threshold)
        self.release_threshold = float(threshold) * float(release_multiplier)
        self.pinching = False

    def reset(self):
        self.pinching = False

    def update(self, hand_landmarks):
        if hand_landmarks is None:
            self.reset()
            return []

        lms = hand_landmarks.landmark
        d = dist(lms[THUMB_TIP], lms[PINKY_TIP])

        if self.pinching:
            is_closed = d < self.release_threshold
        else:
            is_closed = d < self.threshold

        if is_closed:
            if not self.pinching:
                self.pinching = True
                return [GestureEvent("gesture.pinky_pinch", {"dist": d})]
            return []

        self.pinching = False
        return []


class PinkyPinchPlugin:
    def register(self, ctx: AppContext):
        return PluginRegistration(detectors=[PinkyPinchDetector()], actions={})


def plugin():
    return PinkyPinchPlugin()