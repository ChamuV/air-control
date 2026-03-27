# plugins/commands/cursor_multidisplay_toggle.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class CursorMultiDisplayToggleCommandPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:

        def toggle_multi_display_action(event: GestureEvent) -> None:
            ctx.cursor_controller.toggle_multi_display()

        return PluginRegistration(
            detectors=[],
            actions={"cursor.toggle_multidisplay": toggle_multi_display_action},
        )


def plugin():
    return CursorMultiDisplayToggleCommandPlugin()