# src/aircontrol/cursor/controller.py

from __future__ import annotations

from dataclasses import dataclass

import Quartz

from .index_mode import IndexCursorMode
from .palm_mode import PalmCursorMode

from .mapping import map_norm_to_screen
from .smoothing import EMAFilter2D


@dataclass
class DisplayRect:
    display_id: int
    x: float
    y: float
    w: float
    h: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def contains(self, px: float, py: float) -> bool:
        return self.left <= px < self.right and self.top <= py < self.bottom


class CursorController:
    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        mode_name: str = "index",
        enabled: bool = True,
        smoother=None,
        deadzone_px: float = 5.0,
        edge_padding_px: int = 1,
        gain: float = 0.65,
    ):
        if mode_name not in {"palm", "index"}:
            raise ValueError("mode_name must be 'palm' or 'index'")

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.mode_name = mode_name
        self.enabled = enabled

        self.index_mode = IndexCursorMode()
        self.palm_mode = PalmCursorMode()

        self.smoother = smoother or EMAFilter2D(alpha=0.18)

        self.deadzone_px = float(deadzone_px)
        self.edge_padding_px = int(edge_padding_px)
        self.gain = float(gain)

        self._last_output = None

        # Multi-display state
        self.multi_display_enabled = False
        self.displays: list[DisplayRect] = []
        self._refresh_displays()

    def toggle_mode(self) -> None:
        self.mode_name = "index" if self.mode_name == "palm" else "palm"
        self.smoother.reset()
        self._last_output = None

    def toggle_enabled(self) -> None:
        self.enabled = not self.enabled
        self.smoother.reset()
        self._last_output = None

    def toggle_multi_display(self) -> None:
        self.multi_display_enabled = not self.multi_display_enabled
        self._refresh_displays()
        print(f"[cursor] multi-display mode: {self.multi_display_enabled}")

    def get_active_mode(self):
        return self.palm_mode if self.mode_name == "palm" else self.index_mode

    def _refresh_displays(self) -> None:
        self.displays = []

        max_displays = 16
        err, active_displays, display_count = Quartz.CGGetActiveDisplayList(
            max_displays, None, None
        )
        if err != Quartz.kCGErrorSuccess:
            return

        for did in active_displays[:display_count]:
            bounds = Quartz.CGDisplayBounds(did)
            self.displays.append(
                DisplayRect(
                    display_id=int(did),
                    x=float(bounds.origin.x),
                    y=float(bounds.origin.y),
                    w=float(bounds.size.width),
                    h=float(bounds.size.height),
                )
            )

    def _get_current_display_from_last_output(self) -> DisplayRect | None:
        if not self.displays:
            return None

        if self._last_output is None:
            return self.displays[0]

        last_x, last_y = self._last_output
        for display in self.displays:
            if display.contains(last_x, last_y):
                return display

        return self.displays[0]

    def _clamp_to_display(self, px: float, py: float, display: DisplayRect) -> tuple[float, float]:
        m = float(self.edge_padding_px)
        clamped_x = max(display.left + m, min(display.right - 1 - m, px))
        clamped_y = max(display.top + m, min(display.bottom - 1 - m, py))
        return clamped_x, clamped_y

    def _find_neighbor_right(self, current: DisplayRect, py: float) -> DisplayRect | None:
        candidates = [
            d
            for d in self.displays
            if d.display_id != current.display_id
            and d.left >= current.right
            and d.top <= py < d.bottom
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda d: d.left)

    def _find_neighbor_left(self, current: DisplayRect, py: float) -> DisplayRect | None:
        candidates = [
            d
            for d in self.displays
            if d.display_id != current.display_id
            and d.right <= current.left
            and d.top <= py < d.bottom
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda d: d.right)

    def _find_neighbor_down(self, current: DisplayRect, px: float) -> DisplayRect | None:
        candidates = [
            d
            for d in self.displays
            if d.display_id != current.display_id
            and d.top >= current.bottom
            and d.left <= px < d.right
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda d: d.top)

    def _find_neighbor_up(self, current: DisplayRect, px: float) -> DisplayRect | None:
        candidates = [
            d
            for d in self.displays
            if d.display_id != current.display_id
            and d.bottom <= current.top
            and d.left <= px < d.right
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda d: d.bottom)

    def _handle_display_transition(self, px: float, py: float) -> tuple[float, float]:
        current = self._get_current_display_from_last_output()
        if current is None:
            return px, py

        if current.contains(px, py):
            return self._clamp_to_display(px, py, current)

        if not self.multi_display_enabled:
            return self._clamp_to_display(px, py, current)

        # Moving right
        if px >= current.right:
            neighbor = self._find_neighbor_right(current, py)
            if neighbor is not None:
                return self._clamp_to_display(neighbor.left + 2, py, neighbor)
            return self._clamp_to_display(current.right - 1, py, current)

        # Moving left
        if px < current.left:
            neighbor = self._find_neighbor_left(current, py)
            if neighbor is not None:
                return self._clamp_to_display(neighbor.right - 2, py, neighbor)
            return self._clamp_to_display(current.left, py, current)

        # Moving down
        if py >= current.bottom:
            neighbor = self._find_neighbor_down(current, px)
            if neighbor is not None:
                return self._clamp_to_display(px, neighbor.top + 2, neighbor)
            return self._clamp_to_display(px, current.bottom - 1, current)

        # Moving up
        if py < current.top:
            neighbor = self._find_neighbor_up(current, px)
            if neighbor is not None:
                return self._clamp_to_display(px, neighbor.bottom - 2, neighbor)
            return self._clamp_to_display(px, current.top, current)

        return self._clamp_to_display(px, py, current)

    def update_xy(self, hand_landmarks):
        if hand_landmarks is None:
            self.smoother.reset()
            self._last_output = None
            return None

        if not self.enabled:
            return None

        mode = self.get_active_mode()
        point = mode.get_point(hand_landmarks)
        if point is None:
            self.smoother.reset()
            self._last_output = None
            return None

        x_norm, y_norm = point

        px, py = map_norm_to_screen(x_norm, y_norm, self.screen_w, self.screen_h)
        px, py = self.smoother.update(px, py)

        # Reduce sensitivity by compressing movement around previous output
        if self._last_output is not None:
            last_x, last_y = self._last_output
            px = last_x + self.gain * (px - last_x)
            py = last_y + self.gain * (py - last_y)

        px, py = self._handle_display_transition(px, py)

        # Deadzone / stick zone: keep cursor still when hovering near a point
        if self._last_output is not None:
            last_x, last_y = self._last_output
            if abs(px - last_x) < self.deadzone_px and abs(py - last_y) < self.deadzone_px:
                return int(last_x), int(last_y)

        self._last_output = (px, py)
        return int(px), int(py)