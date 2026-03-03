# src/aircontrol/gestures/engine.py

from __future__ import annotations

from .plugin_base import GestureDetector
from .events import GestureEvent


class GestureEngine:
    def __init__(self, detectors: list[GestureDetector]):
        self.detectors = detectors

    def update(self, hand_landmarks) -> list[GestureEvent]:
        """
        Run all detectors for the current frame and
        collect emitted GestureEvents.
        """
        events: list[GestureEvent] = []

        for detector in self.detectors:
            detector_events = detector.update(hand_landmarks)
            if detector_events:
                events.extend(detector_events)

        return events