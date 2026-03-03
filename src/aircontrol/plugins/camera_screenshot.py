# src/aircontrol/plugins/camera_screenshot.py

from __future__ import annotations

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.plugin_base import PluginRegistration
from aircontrol.app_context import AppContext

from aircontrol.actions.camera_screenshot_control import CameraScreenshotController


class CameraScreenshotDetector:
    """
    Gesture:
      - Thumb up
      - Index sideways (TIP/PIP/MCP ~ same y)
      - Pinky sideways (TIP/PIP/MCP ~ same y)
      - Middle + ring folded
    Hold for 5 frames to trigger.
    """

    # Thumb
    THUMB_TIP = 4
    THUMB_IP = 3

    # Index
    INDEX_TIP = 8
    INDEX_PIP = 6
    INDEX_MCP = 5

    # Middle
    MIDDLE_TIP = 12
    MIDDLE_PIP = 10

    # Ring
    RING_TIP = 16
    RING_PIP = 14

    # Pinky
    PINKY_TIP = 20
    PINKY_PIP = 18
    PINKY_MCP = 17

    def __init__(
        self,
        hold_frames: int = 4,
        cooldown_frames: int = 5,
        sideways_y_tol: float = 0.02,
    ):
        self.hold_frames = int(hold_frames)
        self.cooldown_frames = int(cooldown_frames)
        self.sideways_y_tol = float(sideways_y_tol)

        self._hold = 0
        self._cooldown = 0

    def _approx_same_y(self, a, b, c) -> bool:
        # "sideways" ≈ tip/pip/mcp are almost horizontally aligned → y values close
        return (abs(a.y - b.y) < self.sideways_y_tol) and (abs(b.y - c.y) < self.sideways_y_tol)

    def update(self, hand_landmarks) -> list[GestureEvent]:
        if hand_landmarks is None:
            self._hold = 0
            self._cooldown = 0
            return []

        if self._cooldown > 0:
            self._cooldown -= 1
            return []

        lms = hand_landmarks.landmark

        thumb_up = lms[self.THUMB_TIP].y < lms[self.THUMB_IP].y

        index_sideways = self._approx_same_y(
            lms[self.INDEX_TIP], lms[self.INDEX_PIP], lms[self.INDEX_MCP]
        )

        pinky_sideways = self._approx_same_y(
            lms[self.PINKY_TIP], lms[self.PINKY_PIP], lms[self.PINKY_MCP]
        )

        middle_folded = lms[self.MIDDLE_TIP].y > lms[self.MIDDLE_PIP].y
        ring_folded = lms[self.RING_TIP].y > lms[self.RING_PIP].y

        is_screenshot = thumb_up and index_sideways and pinky_sideways and middle_folded and ring_folded

        if is_screenshot:
            self._hold += 1
            if self._hold >= self.hold_frames:
                self._hold = 0
                self._cooldown = self.cooldown_frames
                return [GestureEvent("camera.screenshot", {})]
        else:
            self._hold = 0

        return []


class CameraScreenshotPlugin:
    def register(self, ctx: AppContext) -> PluginRegistration:
        detector = CameraScreenshotDetector()
        shooter = CameraScreenshotController(out_dir="captures")

        def take_screenshot(event: GestureEvent) -> None:
            frame = ctx.latest_frame
            if frame is not None:
                ctx.camera_screenshot.save_frame(frame)

        return PluginRegistration(
            detectors=[detector],
            actions={"camera.screenshot": take_screenshot},
        )


def plugin():
    return CameraScreenshotPlugin()