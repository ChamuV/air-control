# src/aircontrol/plugins/commands/mouse_right_click.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class MouseRightClickCommandPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:

        def right_click_action(event: GestureEvent) -> None:
            ctx.mouse.right_click()

        return PluginRegistration(detectors=[], actions={"mouse.right_click": right_click_action})


def plugin():
    return MouseRightClickCommandPlugin()