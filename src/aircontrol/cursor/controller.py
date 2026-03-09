# src/aircontrol/cursor/controller.py


from .index_mode import IndexCursorMode
from .palm_mode import PalmCursorMode

from .mapping import map_norm_to_screen
from .smoothing import EMAFilter2D

class CursorController:
    def __init__(
            self, 
            screen_w: int, 
            screen_h: int, 
            mode_name: str = "index", 
            enabled: bool = True, 
            smoother = None, 
            deadzone_px: float = 3.0, 
            edge_padding_px: int = 1,
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

        self.deadzone_px = deadzone_px
        self.edge_padding_px = edge_padding_px

        self._last_output = None

    def toggle_mode(self) -> None:
        self.mode_name = "index" if self.mode_name == "palm" else "palm"
        self.smoother.reset()
        self._last_output = None

    def toggle_enabled(self) -> None:
        self.enabled = not self.enabled
        if self.enabled:
            self.smoother.reset()

    def get_active_mode(self):
        return self.palm_mode if self.mode_name == "palm" else self.index_mode
    
    def _clamp_to_screen(self, px: float, py: float) -> tuple[float, float]:
        m = self.edge_padding_px
        px = max(m, min(self.screen_w - m, px))
        py = max(m, min(self.screen_h - m, py))
        return px, py

    def update_xy(self, hand_landmarks):
        """
        Return (x_norm, y_norm) or None.
        """
        if hand_landmarks is None:
            return None
        
        if not self.enabled:
            return None
        
        mode = self.get_active_mode() 
        point = mode.get_point(hand_landmarks)
        if point is None:
            self.smoother.reset()
            return None
        
        x_norm, y_norm = point
        
        px, py = map_norm_to_screen(x_norm, y_norm, self.screen_w, self.screen_h)
        px, py = self.smoother.update(px, py)
        px, py = self._clamp_to_screen(px, py)

        # deadzone check
        if self._last_output is not None:
            last_x, last_y = self._last_output
            if abs(px - last_x) < self.deadzone_px and abs(py - last_y) < self.deadzone_px:
                return int(last_x), int(last_y)  # within deadzone, ignore movement

        self._last_output = (px, py)
        return int(px), int(py)