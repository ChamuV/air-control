# tests/gestures/test_engine.py

from aircontrol.gestures.engine import GestureEngine
from aircontrol.gestures.events import GestureEvent


class DummyDetector:
    def __init__(self, events):
        self.events = events

    def update(self, hand_landmarks):
        return self.events


def test_engine_aggregates_events_from_multiple_detectors():
    detectors = [
        DummyDetector([GestureEvent("gesture.pinch")]),
        DummyDetector([GestureEvent("gesture.fist")]),
    ]

    engine = GestureEngine(detectors=detectors)

    events = engine.update(hand_landmarks="hand")

    assert [e.name for e in events] == ["gesture.pinch", "gesture.fist"]


def test_engine_skips_empty_detector_output():
    detectors = [
        DummyDetector([]),
        DummyDetector([GestureEvent("gesture.fist")]),
        DummyDetector([]),
    ]

    engine = GestureEngine(detectors=detectors)

    events = engine.update(hand_landmarks="hand")

    assert [e.name for e in events] == ["gesture.fist"]


def test_engine_preserves_detector_order():
    detectors = [
        DummyDetector([GestureEvent("gesture.first")]),
        DummyDetector([GestureEvent("gesture.second")]),
        DummyDetector([GestureEvent("gesture.third")]),
    ]

    engine = GestureEngine(detectors=detectors)

    events = engine.update(hand_landmarks="hand")

    assert [e.name for e in events] == [
        "gesture.first",
        "gesture.second",
        "gesture.third",
    ]