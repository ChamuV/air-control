# src/aircontrol/plugins/cursor_move_plugin.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class CursorMoveDetector:
    def __init__(self, cursor):
        self.cursor = cursor

    def update(self, hand_landmarks) -> list[GestureEvent]:
        pos = self.cursor.update_xy(hand_landmarks)
        if pos is None:
            return []

        px, py = pos
        return [GestureEvent("cursor.move", {"x": px, "y": py})]


class CursorMovePlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = CursorMoveDetector(ctx.cursor)

        def move_action(event: GestureEvent) -> None:
            x = event.payload["x"]
            y = event.payload["y"]
            ctx.mouse.move_to(x, y)

        return PluginRegistration(
            detectors=[detector],
            actions={"cursor.move": move_action},
        )
    
def plugin():
    return CursorMovePlugin()