# src/aircontrol/actions/mouse_control.py

import pyautogui


class MouseController:
    def __init__(self, margin_px: int = 8):
        self.margin_px = int(margin_px)
        self.dragging = False

    def _clamp(self, x, y):
        sw, sh = pyautogui.size()
        m = self.margin_px

        cx = int(max(m, min(sw - 1 - m, x)))
        cy = int(max(m, min(sh - 1 - m, y)))
        return cx, cy

    def move_to(self, x, y):
        cx, cy = self._clamp(x, y)

        if self.dragging:
            pyautogui.dragTo(cx, cy, duration=0, button="left")
        else:
            pyautogui.moveTo(cx, cy)

    def click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.click(button="right")

    def scroll(self, clicks: int):
        pyautogui.scroll(int(clicks))

    def mouse_down(self):
        if not self.dragging:
            pyautogui.mouseDown(button="left")
            self.dragging = True

    def mouse_up(self):
        if self.dragging:
            pyautogui.mouseUp(button="left")
            self.dragging = False