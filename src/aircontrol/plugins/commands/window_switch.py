# plugins/commands/window_switch.py

import pyautogui

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class WindowSwitchCommandPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:

        def go_left(event: GestureEvent) -> None:
            pyautogui.hotkey("ctrl", "left")

        def go_right(event: GestureEvent) -> None:
            pyautogui.hotkey("ctrl", "right")

        return PluginRegistration(
            detectors=[],
            actions={
                "window.left": go_left,
                "window.right": go_right,
            },
        )


def plugin():
    return WindowSwitchCommandPlugin()