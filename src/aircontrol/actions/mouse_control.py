# src/aircontrol/actions/mouse_control.py


class MouseController:
    def __init__(self, margin_px: int = 8):
        self.margin_px = int(margin_px)
        self.dragging = False

    def _clamp(self, x, y):
        import pyautogui

        sw, sh = pyautogui.size()
        m = self.margin_px

        cx = int(max(m, min(sw - 1 - m, x)))
        cy = int(max(m, min(sh - 1 - m, y)))
        return cx, cy

    def move_to(self, x, y):
        import pyautogui

        cx, cy = self._clamp(x, y)

        if self.dragging:
            pyautogui.dragTo(cx, cy, duration=0, button="left")
        else:
            pyautogui.moveTo(cx, cy)

    def click(self):
        import pyautogui

        pyautogui.click()

    def right_click(self):
        import pyautogui

        pyautogui.click(button="right")

    def scroll(self, clicks: int):
        import pyautogui

        pyautogui.scroll(int(clicks))

    def mouse_down(self):
        import pyautogui

        if not self.dragging:
            pyautogui.mouseDown(button="left")
            self.dragging = True

    def mouse_up(self):
        import pyautogui

        if self.dragging:
            pyautogui.mouseUp(button="left")
            self.dragging = False