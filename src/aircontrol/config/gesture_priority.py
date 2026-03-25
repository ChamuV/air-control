# config/gesture_priority.py

import yaml
from pathlib import Path


class GesturePriority:
    def __init__(self, path: str):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Priority YAML not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        self.priorities = data.get("priorities", {})

    def get(self, gesture_name: str) -> int:
        return self.priorities.get(gesture_name, 0)


class PriorityResolver:
    def __init__(self, priority_map: GesturePriority):
        self.priority_map = priority_map

    def resolve(self, events):
        gesture_events = [e for e in events if e.name.startswith("gesture.")]
        other_events = [e for e in events if not e.name.startswith("gesture.")]

        if not gesture_events:
            return events

        top = max(
            gesture_events,
            key=lambda e: self.priority_map.get(e.name),
        )

        return [top] + other_events