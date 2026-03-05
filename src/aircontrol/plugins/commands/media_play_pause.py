# src/aircontrol/plugins/commands/media_play_pause.py

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class MediaPlayPauseCommandPlugin:
    """Command-only plugin: media.play_pause"""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def play_pause_action(event: GestureEvent) -> None:
            ctx.media.toggle_play_pause()

        return PluginRegistration(
            detectors=[],
            actions={"media.play_pause": play_pause_action},
        )


def plugin():
    return MediaPlayPauseCommandPlugin()