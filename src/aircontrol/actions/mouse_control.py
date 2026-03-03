# src/aircontrol/actions/mouse_control.py

import pyautogui


class MouseController:
    def move_to(self, x, y):
        pyautogui.moveTo(x, y)

    def click(self):
        pyautogui.click()