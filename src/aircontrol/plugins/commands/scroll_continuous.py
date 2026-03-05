# src/aircontrol/plugins/commands/scroll_continuous.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class ScrollContinuousCommandPlugin:
    """Command-only plugin: scroll.continuous"""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def scroll_action(event: GestureEvent) -> None:
            direction = event.payload.get("direction")
            amount = int(event.payload.get("amount", 1))

            # Keep your existing convention:
            # ctx.mouse.scroll(positive) scrolls up, negative scrolls down (PyAutoGUI style)
            if direction == "down":
                ctx.mouse.scroll(-amount)
            else:
                ctx.mouse.scroll(amount)

        return PluginRegistration(
            detectors=[],
            actions={"scroll.continuous": scroll_action},
        )


def plugin():
    return ScrollContinuousCommandPlugin()