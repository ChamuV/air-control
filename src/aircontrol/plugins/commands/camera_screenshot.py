# src/aircontrol/plugins/commands/camera_screenshot.py

from __future__ import annotations

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration


class CameraScreenshotCommandPlugin:
    """Command-only plugin: camera.screenshot"""
    def register(self, ctx: AppContext) -> PluginRegistration:

        def take_screenshot(event: GestureEvent) -> None:
            frame = ctx.latest_frame
            if frame is not None:
                ctx.camera_screenshot.save_frame(frame)

        return PluginRegistration(
            detectors=[],
            actions={"camera.screenshot": take_screenshot},
        )


def plugin():
    return CameraScreenshotCommandPlugin()