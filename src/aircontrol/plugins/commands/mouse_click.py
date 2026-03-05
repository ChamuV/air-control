# src/aircontrol/plugins/commands/mouse_click.py

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext


class MouseClickCommandPlugin:
    """Command-only plugin: implements mouse.click action."""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def mouse_click(event: GestureEvent) -> None:
            ctx.mouse.click()

        return PluginRegistration(
            detectors=[],
            actions={"mouse.click": mouse_click},
        )


def plugin():
    return MouseClickCommandPlugin()