# plugins/commands/cursor_multidisplay_toggle.py

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class CursorMultiDisplayToggleCommandPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        def toggle_multi_display(event: GestureEvent) -> None:
            if hasattr(ctx, "cursor_controller") and ctx.cursor_controller is not None:
                ctx.cursor_controller.toggle_multi_display()

        return PluginRegistration(
            commands={
                "cursor.toggle_multidisplay": toggle_multi_display,
            }
        )


def plugin():
    return CursorMultiDisplayToggleCommandPlugin()