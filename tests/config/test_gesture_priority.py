# tests/config/test_gesture_priority.py

from pathlib import Path

from aircontrol.config.gesture_priority import GesturePriority, PriorityResolver
from aircontrol.gestures.events import GestureEvent


def make_priority_map(tmp_path: Path, yaml_body: str) -> GesturePriority:
    path = tmp_path / "gesture_priority.yaml"
    path.write_text(yaml_body.strip())
    return GesturePriority(str(path))


def test_gesture_priority_loads_values(tmp_path: Path):
    priority_map = make_priority_map(
        tmp_path,
        """
profile: default

priorities:
  gesture.fist: 70
  gesture.open_palm_hold: 60
""",
    )

    assert priority_map.get("gesture.fist") == 70
    assert priority_map.get("gesture.open_palm_hold") == 60


def test_gesture_priority_unknown_defaults_to_zero(tmp_path: Path):
    priority_map = make_priority_map(
        tmp_path,
        """
profile: default

priorities:
  gesture.fist: 70
""",
    )

    assert priority_map.get("gesture.unknown") == 0


def test_priority_resolver_keeps_highest_priority_gesture(tmp_path: Path):
    priority_map = make_priority_map(
        tmp_path,
        """
profile: default

priorities:
  gesture.fist: 70
  gesture.open_palm_hold: 60
  gesture.pinch: 50
""",
    )

    resolver = PriorityResolver(priority_map)

    events = [
        GestureEvent("gesture.pinch"),
        GestureEvent("gesture.fist"),
        GestureEvent("gesture.open_palm_hold"),
    ]

    resolved = resolver.resolve(events)

    assert len(resolved) == 1
    assert resolved[0].name == "gesture.fist"


def test_priority_resolver_keeps_non_gesture_events(tmp_path: Path):
    priority_map = make_priority_map(
        tmp_path,
        """
profile: default

priorities:
  gesture.fist: 70
  gesture.open_palm_hold: 60
""",
    )

    resolver = PriorityResolver(priority_map)

    events = [
        GestureEvent("gesture.open_palm_hold"),
        GestureEvent("cursor.move", payload={"x": 100, "y": 200}),
        GestureEvent("gesture.fist"),
    ]

    resolved = resolver.resolve(events)

    names = [e.name for e in resolved]

    assert "gesture.fist" in names
    assert "cursor.move" in names
    assert "gesture.open_palm_hold" not in names
    assert len(resolved) == 2


def test_priority_resolver_returns_all_if_no_gestures(tmp_path: Path):
    priority_map = make_priority_map(
        tmp_path,
        """
profile: default

priorities:
  gesture.fist: 70
""",
    )

    resolver = PriorityResolver(priority_map)

    events = [
        GestureEvent("cursor.move"),
        GestureEvent("scroll"),
    ]

    resolved = resolver.resolve(events)

    assert resolved == events


def test_priority_resolver_tie_keeps_first(tmp_path: Path):
    priority_map = make_priority_map(
        tmp_path,
        """
profile: default

priorities:
  gesture.fist: 70
  gesture.open_palm_hold: 70
""",
    )

    resolver = PriorityResolver(priority_map)

    events = [
        GestureEvent("gesture.fist"),
        GestureEvent("gesture.open_palm_hold"),
    ]

    resolved = resolver.resolve(events)

    assert len(resolved) == 1
    assert resolved[0].name == "gesture.fist"