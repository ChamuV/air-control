# src/aircontrol/actions/volume_control.py

import subprocess


class VolumeControllerMacOS:
    """
    Reliable macOS volume control using osascript.
    Volume is in [0, 100].
    """

    def __init__(self, delta_per_step: int = 4):
        self.delta_per_step = int(delta_per_step)

    def _osascript(self, script: str) -> str:
        p = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
        if p.returncode != 0:
            raise RuntimeError(p.stderr.strip() or p.stdout.strip())
        return (p.stdout or "").strip()

    def get_volume(self) -> int:
        return int(self._osascript("output volume of (get volume settings)"))

    def set_volume(self, v: int) -> None:
        v = max(0, min(100, int(v)))
        self._osascript(f"set volume output volume {v}")

    def change(self, direction: str, steps: int) -> int:
        """
        direction: "up" or "down"
        steps: positive integer
        Returns the new volume.
        """
        steps = max(1, int(steps))
        current = self.get_volume()

        delta = self.delta_per_step * steps
        if direction == "down":
            delta = -delta

        new_v = max(0, min(100, current + delta))
        self.set_volume(new_v)
        return new_v