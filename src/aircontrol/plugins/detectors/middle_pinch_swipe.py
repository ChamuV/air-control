# src/aircontrol/plugins/detectors/middle_pinch_swipe.py

from __future__ import annotations

from typing import Optional

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.tracking.hand_landmarks import THUMB_TIP, MIDDLE_TIP, dist


class MiddlePinchSwipeDetector:
    """
    Hold middle pinch, then move horizontally to emit repeated left/right
    switch events while the pinch remains closed.

    Each time enough horizontal movement is accumulated, emit one event and
    reset the anchor point so continued movement can emit again.
    """

    def __init__(
        self,
        pinch_threshold: float = 0.045,
        release_multiplier: float = 1.2,
        swipe_dx_threshold: float = 0.08,
    ):
        self.threshold = float(pinch_threshold)
        self.release_threshold = float(pinch_threshold) * float(release_multiplier)
        self.swipe_dx_threshold = float(swipe_dx_threshold)

        self.pinching = False
        self.anchor_x: Optional[float] = None

    def reset(self):
        self.pinching = False
        self.anchor_x = None

    def update(self, hand_landmarks):
        if hand_landmarks is None:
            self.reset()
            return []

        lms = hand_landmarks.landmark
        d = dist(lms[THUMB_TIP], lms[MIDDLE_TIP])
        current_x = lms[MIDDLE_TIP].x

        if self.pinching:
            is_closed = d < self.release_threshold
        else:
            is_closed = d < self.threshold

        if not is_closed:
            self.reset()
            return []

        # pinch just started
        if not self.pinching:
            self.pinching = True
            self.anchor_x = current_x
            return []

        # pinch held: emit repeatedly as hand keeps moving
        if self.anchor_x is None:
            self.anchor_x = current_x
            return []

        dx = current_x - self.anchor_x

        if dx >= self.swipe_dx_threshold:
            self.anchor_x = current_x
            return [GestureEvent("gesture.middle_pinch_swipe_right")]

        if dx <= -self.swipe_dx_threshold:
            self.anchor_x = current_x
            return [GestureEvent("gesture.middle_pinch_swipe_left")]

        return []


class MiddlePinchSwipePlugin:
    def register(self, ctx: AppContext):
        return PluginRegistration(detectors=[MiddlePinchSwipeDetector()], actions={})


def plugin():
    return MiddlePinchSwipePlugin()