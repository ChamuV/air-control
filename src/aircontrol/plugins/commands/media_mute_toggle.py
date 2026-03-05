# src/aircontrol/plugins/commands/media_mute_toggle.py

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class MediaMuteToggleCommandPlugin:
    """Command-only plugin: media.mute_toggle"""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def mute_action(event: GestureEvent) -> None:
            ctx.media.toggle_mute()

        return PluginRegistration(
            detectors=[],
            actions={"media.mute_toggle": mute_action},
        )


def plugin():
    return MediaMuteToggleCommandPlugin()