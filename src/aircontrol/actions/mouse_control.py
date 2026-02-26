# src/aircontrol/actions/mouse_control.py

import pyautogui
import math


class MouseController:
    def __init__(
        self,
        dead_zone: int = 10,
        smoothing: float = 0.2,
        mirror_x: bool = True,   
        mirror_y: bool = False,  
    ):
        self.screen_width, self.screen_height = pyautogui.size()
        self.dead_zone = dead_zone
        self.smoothing = smoothing
        self.mirror_x = mirror_x
        self.mirror_y = mirror_y

        self.prev_x, self.prev_y = pyautogui.position()

    def move_to_norm(self, norm_x: float, norm_y: float):
        if self.mirror_x:
            norm_x = 1.0 - norm_x
        if self.mirror_y:
            norm_y = 1.0 - norm_y

        target_x = int(norm_x * self.screen_width)
        target_y = int(norm_y * self.screen_height)

        dx = target_x - self.prev_x
        dy = target_y - self.prev_y

        if math.hypot(dx, dy) < self.dead_zone:
            return

        smooth_x = int(self.prev_x + dx * self.smoothing)
        smooth_y = int(self.prev_y + dy * self.smoothing)

        pyautogui.moveTo(smooth_x, smooth_y)

        self.prev_x, self.prev_y = smooth_x, smooth_y