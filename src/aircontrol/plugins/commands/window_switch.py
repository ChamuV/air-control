# plugins/commands/window_switch.py

import time
import pyautogui

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class WindowSwitchCommandPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:

        last_time = {"left": 0.0, "right": 0.0}
        min_interval = 0.1  # seconds between switches

        def go_left(event: GestureEvent) -> None:
            now = time.time()
            if now - last_time["left"] < min_interval:
                return
            last_time["left"] = now

            pyautogui.hotkey("ctrl", "left")

        def go_right(event: GestureEvent) -> None:
            now = time.time()
            if now - last_time["right"] < min_interval:
                return
            last_time["right"] = now

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