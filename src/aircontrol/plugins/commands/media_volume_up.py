# plugins/commands/media_volume_up.py

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class MediaVolumeUpCommandPlugin:
    """Command-only plugin: media.volume_up"""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def volume_up_action(event: GestureEvent) -> None:
            ctx.media.volume_up(1)

        return PluginRegistration(
            detectors=[],
            actions={"media.volume_up": volume_up_action},
        )


def plugin():
    return MediaVolumeUpCommandPlugin()