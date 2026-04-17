# src/aircontrol/plugins/commands/scroll_continuous.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class ScrollContinuousCommandPlugin:
    def register(self, ctx: AppContext):
        scrolling = False

        def scroll_start(event: GestureEvent) -> None:
            nonlocal scrolling
            scrolling = True

        def scroll_action(event: GestureEvent) -> None:
            nonlocal scrolling
            if not scrolling:
                return

            direction = event.payload.get("direction", "up")
            amount = max(1, int(event.payload.get("amount", 1)))

            if direction == "down":
                ctx.mouse.scroll(-amount)
            else:
                ctx.mouse.scroll(amount)

        def scroll_end(event: GestureEvent) -> None:
            nonlocal scrolling
            scrolling = False

        return PluginRegistration(
            detectors=[],
            actions={
                "scroll.start": scroll_start,
                "scroll.continuous": scroll_action,
                "scroll.end": scroll_end,
            },
        )


def plugin():
    return ScrollContinuousCommandPlugin()