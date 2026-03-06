# src/aircontrol/plugins/detectors/ring_pinch.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.tracking.hand_landmarks import (
    THUMB_TIP,
    RING_TIP,
    dist,
)


class RingPinchDetector:

    def __init__(self, pinch_threshold: float = 0.04):
        self.threshold = pinch_threshold
        self.pinching = False

    def update(self, hand_landmarks):
        if hand_landmarks is None:
            if self.pinching:
                self.pinching = False
                return [GestureEvent("gesture.ring_pinch.end")]
            return []

        lms = hand_landmarks.landmark
        d = dist(lms, THUMB_TIP, RING_TIP)

        events = []

        if d < self.threshold:

            if not self.pinching:
                self.pinching = True
                events.append(GestureEvent("gesture.ring_pinch.start"))

            events.append(GestureEvent("gesture.ring_pinch.move"))

        else:

            if self.pinching:
                self.pinching = False
                events.append(GestureEvent("gesture.ring_pinch.end"))

        return events


class RingPinchPlugin:

    def register(self, ctx: AppContext):
        return PluginRegistration(
            detectors=[RingPinchDetector()],
            actions={}
        )


def plugin():
    return RingPinchPlugin()