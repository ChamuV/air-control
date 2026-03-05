# src/aircontrol/plugins/commands/cursor_move.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class CursorMoveCommandPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:

        def move_action(event: GestureEvent) -> None:
            x = event.payload["x"]
            y = event.payload["y"]
            ctx.mouse.move_to(x, y)

        return PluginRegistration(detectors=[], actions={"cursor.move": move_action})


def plugin():
    return CursorMoveCommandPlugin()