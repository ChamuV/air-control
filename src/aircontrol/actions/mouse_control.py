# src/aircontrol/actions/mouse_control.py

import pyautogui


class MouseController:
    def move_to(self, x, y):
        pyautogui.moveTo(x, y)

    def click(self):
        pyautogui.click()

    def scroll(self, clicks: int):
        """
        Scroll vertically.
        Positive -> scroll up
        Negative -> scroll down
        """
        pyautogui.scroll(int(clicks))