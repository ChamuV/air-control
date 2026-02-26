# src/aircontrol/actions/volume_control.py

import subprocess 
import pyautogui

class VolumeController:
    """
    macOS: uses osascript to set/get output volume (0..100).
    Fallback: sends volumeup/volumedown keys via pyautogui (may depend on OS).
    """

    def __init__(self, step: int = 2):
        self.step = int(step)

    def _run_osascript(self, script: str) -> str:
        out = subprocess.check_output(["osascript", "-e", script], text=True).strip()
        return out
    
    def get_volume(self) -> int:
        try:
            v = self._run_osascript("output volume of (get volume settings)")
            return int(v)
        except Exception:
            return -1 # if not supported, we can't read volume
        
    def set_volume(self, volume_0_100: int):
        v = max(0, min(100, int(volume_0_100)))
        try:
            self._run_osascript(f"set volume output volume {v}")
        except Exception:
            # fallback: approximate using key presses
            # NOTE: can't set absolute volume with this fallback
            pass

    def volume_up(self, steps: int = 1):
        steps = max(1, int(steps))
        v = self.get_volume()
        if v >= 0:
            self.set_volume(v + self.step * steps)
            return

        # fallback
        for _ in range(steps):
            pyautogui.press("volumeup")

    def volume_down(self, steps: int = 1):
        steps = max(1, int(steps))
        v = self.get_volume()
        if v >= 0:
            self.set_volume(v - self.step * steps)
            return

        # fallback
        for _ in range(steps):
            pyautogui.press("volumedown")