# src/aircontrol/actions/media_control.py

from AppKit import NSEvent
from Quartz import CGEventPost, kCGHIDEventTap
import subprocess
import time


NX_SYSDEFINED = 14
NX_SUBTYPE_AUX_CONTROL_BUTTONS = 8

NX_KEYTYPE_PLAY = 16
NX_KEYTYPE_MUTE = 7


class MediaControllerMacOS:
    def __init__(self, volume_delta_per_step: int = 4):
        self.volume_delta_per_step = int(volume_delta_per_step)

    def _media_key_event(self, key: int, key_down: bool):
        flags = 0xA00

        if key_down:
            data1 = (key << 16) | flags
        else:
            data1 = (key << 16) | (flags | 0x100)

        return NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
            NX_SYSDEFINED,
            (0, 0),
            0,
            0.0,
            0,
            None,
            NX_SUBTYPE_AUX_CONTROL_BUTTONS,
            data1,
            -1,
        )

    def _tap_key(self, key: int) -> None:
        ev_down = self._media_key_event(key, True)
        ev_up = self._media_key_event(key, False)
        CGEventPost(kCGHIDEventTap, ev_down.CGEvent())
        time.sleep(0.02)
        CGEventPost(kCGHIDEventTap, ev_up.CGEvent())

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

    def change_volume(self, direction: str, steps: int = 1) -> int:
        steps = max(1, int(steps))
        current = self.get_volume()

        delta = self.volume_delta_per_step * steps
        if direction == "down":
            delta = -delta

        new_v = max(0, min(100, current + delta))
        self.set_volume(new_v)
        return new_v

    def volume_up(self, steps: int = 1) -> int:
        return self.change_volume("up", steps)

    def volume_down(self, steps: int = 1) -> int:
        return self.change_volume("down", steps)

    def toggle_play_pause(self) -> None:
        self._tap_key(NX_KEYTYPE_PLAY)

    def toggle_mute(self) -> None:
        self._tap_key(NX_KEYTYPE_MUTE)