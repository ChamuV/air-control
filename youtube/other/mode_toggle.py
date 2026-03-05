# src/aircontrol/plugins/mode_toggle.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent 
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

class ModeToggleDetector:
    # Finger landmark indices
    INDEX_TIP = 8
    INDEX_PIP = 6

    MIDDLE_TIP = 12
    MIDDLE_PIP = 10

    RING_TIP = 16
    RING_PIP = 14

    PINKY_TIP = 20
    PINKY_PIP = 18

    def __init__(self, cooldown_frames: int = 5):
        self.cooldown_frames = int(cooldown_frames)
        self._cooldown = 0

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None: 
            self._cooldown = 0
            return []
        
        if self._cooldown > 0:
            self._cooldown -= 1
            return []
        
        lms = hand_landmarks.landmark

        # finger extension check
        index_extended = lms[self.INDEX_TIP].y < lms[self.INDEX_PIP].y
        middle_extended = lms[self.MIDDLE_TIP].y < lms[self.MIDDLE_PIP].y
        ring_extended = lms[self.RING_TIP].y < lms[self.RING_PIP].y
        pinky_extended = lms[self.PINKY_TIP].y < lms[self.PINKY_PIP].y

        is_two_finger = (
            index_extended
            and middle_extended
            and  (not ring_extended)
            and (not pinky_extended)
        )

        if is_two_finger:
            self._cooldown = self.cooldown_frames
            return [GestureEvent("cursor.toggle_mode", {})]
        
        return []
    

class ModeTogglePlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = ModeToggleDetector()

        def toggle_action(event: GestureEvent) -> None:
            ctx.cursor.toggle_mode()

        return PluginRegistration(
            detectors=[detector],
            actions={"cursor.toggle_mode": toggle_action},
        )


def plugin():
    return ModeTogglePlugin()