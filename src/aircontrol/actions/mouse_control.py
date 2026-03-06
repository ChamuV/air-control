# src/aircontrol/actions/mouse_control.py

import pyautogui


class MouseController:
    def __init__(self, margin_px: int = 8):
        self.margin_px = int(margin_px)

    def move_to(self, x, y):
        sw, sh = pyautogui.size()
        m = self.margin_px

        cx = int(max(m, min(sw - 1 - m, x)))
        cy = int(max(m, min(sh - 1 - m, y)))

        pyautogui.moveTo(cx, cy)

    def click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.click(button="right")

    def scroll(self, clicks: int):
        """
        Scroll vertically.
        Positive -> scroll up
        Negative -> scroll down
        """
        pyautogui.scroll(int(clicks))

    def mouse_down(self):
        pyautogui.mouseDown()

    def mouse_up(self):
        pyautogui.mouseUp()