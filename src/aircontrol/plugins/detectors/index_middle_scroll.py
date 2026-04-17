# src/aircontrol/plugins/detectors/index_middle_scroll.py

from __future__ import annotations

from typing import Optional

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.tracking.hand_landmarks import INDEX_TIP, MIDDLE_TIP, dist


class IndexMiddleScrollDetector:
    """
    Hold index-middle pinch for a few frames to enter scroll mode.
    While pinched, vertical movement controls scroll.
    Release exits scroll mode.
    """

    def __init__(
        self,
        pinch_threshold: float = 0.05,
        release_multiplier: float = 1.2,
        hold_frames: int = 3,
        move_deadzone: float = 0.008,
        scroll_gain: float = 180.0,
    ):
        self.threshold = float(pinch_threshold)
        self.release_threshold = float(pinch_threshold) * float(release_multiplier)
        self.hold_frames = int(hold_frames)
        self.move_deadzone = float(move_deadzone)
        self.scroll_gain = float(scroll_gain)

        self.pinching = False
        self.scrolling = False
        self.hold_counter = 0
        self.baseline_y: Optional[float] = None

    def reset(self):
        self.pinching = False
        self.scrolling = False
        self.hold_counter = 0
        self.baseline_y = None

    def update(self, hand_landmarks):
        if hand_landmarks is None:
            events = []
            if self.scrolling:
                events.append(GestureEvent("gesture.index_middle_scroll.end", {}))
            self.reset()
            return events

        lms = hand_landmarks.landmark
        d = dist(lms[INDEX_TIP], lms[MIDDLE_TIP])
        current_y = 0.5 * (lms[INDEX_TIP].y + lms[MIDDLE_TIP].y)

        if self.pinching:
            is_closed = d < self.release_threshold
        else:
            is_closed = d < self.threshold

        if not is_closed:
            events = []
            if self.scrolling:
                events.append(GestureEvent("gesture.index_middle_scroll.end", {}))
            self.reset()
            return events

        if not self.pinching:
            self.pinching = True
            self.hold_counter = 1
            return []

        if not self.scrolling:
            self.hold_counter += 1
            if self.hold_counter < self.hold_frames:
                return []
            self.scrolling = True
            self.baseline_y = current_y
            return [GestureEvent("gesture.index_middle_scroll.start", {})]

        if self.baseline_y is None:
            self.baseline_y = current_y
            return []

        dy = current_y - self.baseline_y

        if abs(dy) < self.move_deadzone:
            return []

        amount = max(1, int(abs(dy) * self.scroll_gain))
        direction = "down" if dy > 0 else "up"
        self.baseline_y = current_y

        return [
            GestureEvent(
                "gesture.index_middle_scroll.move",
                {"direction": direction, "amount": amount},
            )
        ]


class IndexMiddleScrollPlugin:
    def register(self, ctx: AppContext):
        return PluginRegistration(detectors=[IndexMiddleScrollDetector()], actions={})


def plugin():
    return IndexMiddleScrollPlugin()