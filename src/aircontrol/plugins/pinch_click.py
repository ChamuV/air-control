# src/aircontrol/plugins/pinch_click.py

import math

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration

from aircontrol.app_context import AppContext


class PinchClickDetector:

    THUMB_TIP_ID = 4
    INDEX_TIP_ID = 8

    def __init__(self, threshold: float = 0.04, cooldown_frames: int = 8):
        self.threshold = threshold
        self.cooldown_frames = cooldown_frames
        self._cooldown = 0

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        thumb = lms[self.THUMB_TIP_ID]
        index = lms[self.INDEX_TIP_ID]

        dx = thumb.x - index.x
        dy = thumb.y - index.y
        dist = math.hypot(dx, dy)

        if dist < self.threshold:
            self._cooldown = self.cooldown_frames
            return [GestureEvent("mouse.click", {})]

        return []


class PinchClickPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = PinchClickDetector()

        def click_action(event: GestureEvent) -> None:
            ctx.mouse.click()
        
        return PluginRegistration(
                detectors=[detector],
                actions={"mouse.click": click_action}
        )
    
def plugin():
    return PinchClickPlugin()