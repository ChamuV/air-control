# src/aircontrol/plugins/detectors/pinch.py

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.tracking.hand_landmarks import THUMB_TIP, INDEX_TIP, dist

class PinchDetector:
    def __init__(self, threshold: float = 0.05, cooldown_frames: int = 4):
        self.threshold = float(threshold)
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
        d = dist(lms[THUMB_TIP], lms[INDEX_TIP])

        if d < self.threshold:
            self._cooldown = self.cooldown_frames
            return [GestureEvent("gesture.pinch", {"dist": d})]
        
        return []
    
class PinchPlugin:
    """Detector-only plugin: emits gesture.pinch events."""
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = PinchDetector()
        return PluginRegistration(detectors=[detector], actions={})


def plugin():
    return PinchPlugin()