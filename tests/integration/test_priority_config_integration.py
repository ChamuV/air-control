# tests/integration/test_priority_config_integration.py

from pathlib import Path

from aircontrol.config.gesture_priority import GesturePriority, PriorityResolver
from aircontrol.gestures.events import GestureEvent


def test_real_priority_yaml_prefers_highest_priority_gesture():
    repo_root = Path(__file__).resolve().parents[2]
    priority_path = repo_root / "src" / "aircontrol" / "config" / "gesture_priority.yaml"

    resolver = PriorityResolver(GesturePriority(str(priority_path)))
    events = [
        GestureEvent("gesture.pinch"),
        GestureEvent("cursor.move", {"x": 10, "y": 20}),
        GestureEvent("gesture.vulcan_salute"),
    ]

    resolved = resolver.resolve(events)
    names = [e.name for e in resolved]

    assert names[0] == "gesture.vulcan_salute"
    assert "cursor.move" in names
    assert "gesture.pinch" not in names
