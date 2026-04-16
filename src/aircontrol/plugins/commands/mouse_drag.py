# src/aircontrol/plugins/commands/mouse_drag.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class MouseDragCommandPlugin:
    def register(self, ctx: AppContext):
        dragging = False

        def start_drag(event: GestureEvent):
            nonlocal dragging
            if not dragging:
                ctx.mouse.mouse_down()
                dragging = True

        def move_drag(event: GestureEvent):
            # cursor movement is already handled by cursor.move
            pass

        def end_drag(event: GestureEvent):
            nonlocal dragging
            if dragging:
                ctx.mouse.mouse_up()
                dragging = False

        return PluginRegistration(
            detectors=[],
            actions={
                "drag.start": start_drag,
                "drag.move": move_drag,
                "drag.end": end_drag,
            }
        )


def plugin():
    return MouseDragCommandPlugin()