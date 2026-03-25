# plugins/commands/media_volume_down.py

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class MediaVolumeDownCommandPlugin:
    """Command-only plugin: media.volume_down"""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def volume_down_action(event: GestureEvent) -> None:
            ctx.volume.change("down", 1)

        return PluginRegistration(
            detectors=[],
            actions={"media.volume_down": volume_down_action},
        )


def plugin():
    return MediaVolumeDownCommandPlugin()