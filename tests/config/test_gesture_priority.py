# tests/config/test_gesture_priority.py

from pathlib import Path

import pytest

from aircontrol.config.gesture_priority import GesturePriority, PriorityResolver
from aircontrol.gestures.events import GestureEvent

def test_priority_file_missing():
    with pytest.raises(FileNotFoundError):
        GesturePriority("non_existent.yaml")


from pathlib import Path

from aircontrol.config.gesture_priority import GesturePriority, PriorityResolver
from aircontrol.gestures.events import GestureEvent


def test_gesture_priority_loads_values(tmp_path: Path):
    priority_file = tmp_path / "gesture_priority.yaml"
    priority_file.write_text(
        """
priorities:
  gesture.fist: 70
  gesture.open_palm_hold: 60
"""
    )

    priority_map = GesturePriority(str(priority_file))

    assert priority_map.get("gesture.fist") == 70
    assert priority_map.get("gesture.open_palm_hold") == 60
    assert priority_map.get("gesture.unknown") == 0


def test_priority_resolver_keeps_highest_priority_gesture():
    class DummyPriorityMap:
        def get(self, gesture_name: str) -> int:
            values = {
                "gesture.fist": 70,
                "gesture.open_palm_hold": 60,
                "gesture.vulcan_salute": 120,
            }
            return values.get(gesture_name, 0)

    resolver = PriorityResolver(DummyPriorityMap())

    events = [
        GestureEvent("gesture.fist", {}),
        GestureEvent("gesture.open_palm_hold", {}),
        GestureEvent("gesture.vulcan_salute", {}),
        GestureEvent("cursor.move", {"x": 100, "y": 200}),
    ]

    resolved = resolver.resolve(events)

    assert len(resolved) == 2
    assert resolved[0].name == "gesture.vulcan_salute"
    assert resolved[1].name == "cursor.move"


def test_priority_resolver_returns_original_events_when_no_gesture_events():
    class DummyPriorityMap:
        def get(self, gesture_name: str) -> int:
            return 0

    resolver = PriorityResolver(DummyPriorityMap())

    events = [
        GestureEvent("cursor.move", {"x": 10, "y": 20}),
        GestureEvent("mouse.click", {}),
    ]

    resolved = resolver.resolve(events)

    assert resolved == events