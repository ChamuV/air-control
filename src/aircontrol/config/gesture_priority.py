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
        self.drag_active = False
        self.scroll_active = False

    def _resolve_normal(self, events):
        gesture_events = [e for e in events if e.name.startswith("gesture.")]
        other_events = [e for e in events if not e.name.startswith("gesture.")]

        if not gesture_events:
            return events

        top = max(
            gesture_events,
            key=lambda e: self.priority_map.get(e.name),
        )

        return [top] + other_events

    def resolve(self, events):
        if not events:
            return []

        gesture_events = [e for e in events if e.name.startswith("gesture.")]
        gesture_names = {e.name for e in gesture_events}

        # DRAG LOCK
        if self.drag_active:
            allowed = []

            for e in events:
                if e.name in {
                    "gesture.ring_pinch.move",
                    "gesture.ring_pinch.end",
                    "cursor.move",
                }:
                    allowed.append(e)

            if "gesture.ring_pinch.end" in gesture_names:
                self.drag_active = False

            return allowed

        # SCROLL LOCK (index-middle pinch scroll)
        if self.scroll_active:
            allowed = []

            for e in events:
                if e.name in {
                    "gesture.index_middle_scroll.move",
                    "gesture.index_middle_scroll.end",
                    "cursor.move",
                }:
                    allowed.append(e)

            if "gesture.index_middle_scroll.end" in gesture_names:
                self.scroll_active = False

            return allowed

        # NORMAL PRIORITY RESOLUTION
        resolved = self._resolve_normal(events)
        resolved_names = {e.name for e in resolved}

        # Enter drag lock
        if "gesture.ring_pinch.start" in resolved_names:
            self.drag_active = True
            return [
                e for e in resolved
                if e.name in {"gesture.ring_pinch.start", "cursor.move"}
            ]

        # Enter scroll lock
        if "gesture.index_middle_scroll.start" in resolved_names:
            self.scroll_active = True
            return [
                e for e in resolved
                if e.name in {"gesture.index_middle_scroll.start", "cursor.move"}
            ]

        return resolved