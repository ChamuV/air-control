# src/aircontrol/plugins/commands/call_start.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.actions.facetime_control import FaceTimeControllerMacOS


class CallStartCommandPlugin:
    """
    Command: call.start
    """

    def register(self, ctx: AppContext) -> PluginRegistration:

        def call_action(event: GestureEvent) -> None:
            number = event.payload.get("number", "+919845103831")
            mode = event.payload.get("mode", "video")

            facetime = FaceTimeControllerMacOS(
                phone_number_str=number,
                mode=mode,
            )
            facetime.call()

        return PluginRegistration(
            detectors=[],
            actions={"call.start": call_action},
        )


def plugin():
    return CallStartCommandPlugin()