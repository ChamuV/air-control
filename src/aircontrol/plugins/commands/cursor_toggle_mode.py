# src/aircontrol/plugins/commands/cursor_toggle_mode.py

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class CursorToggleModeCommandPlugin:
    """Command-only plugin: cursor.toggle_mode"""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def toggle_action(event: GestureEvent) -> None:
            ctx.cursor.toggle_mode()

        return PluginRegistration(
            detectors=[],
            actions={"cursor.toggle_mode": toggle_action},
        )


def plugin():
    return CursorToggleModeCommandPlugin()