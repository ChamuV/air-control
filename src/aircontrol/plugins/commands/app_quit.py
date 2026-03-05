# src/aircontrol/plugins/commands/app_quit.py

import sys

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class AppQuitCommandPlugin:
    """Command-only plugin: implements app.quit action."""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def quit_action(event: GestureEvent) -> None:
            print("Quitting AirControl...")
            sys.exit(0)

        return PluginRegistration(
            detectors=[],
            actions={"app.quit": quit_action},
        )


def plugin():
    return AppQuitCommandPlugin()