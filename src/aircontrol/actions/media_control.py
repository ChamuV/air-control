# src/aircontrol/actions/media_control.py

from AppKit import NSEvent
from Quartz import CGEventPost, kCGHIDEventTap
import time


NX_SYSDEFINED = 14
NX_SUBTYPE_AUX_CONTROL_BUTTONS = 8

NX_KEYTYPE_PLAY = 16
NX_KEYTYPE_MUTE = 7


class MediaControllerMacOS:
    def _media_key_event(self, key: int, key_down: bool):
        flags = 0xA00

        if key_down:
            data1 = (key << 16) | flags
        else:
            data1 = (key << 16) | (flags | 0x100)

        return NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
            NX_SYSDEFINED,                  # type
            (0, 0),                         # location
            0,                              # modifierFlags
            0.0,                            # timestamp
            0,                              # windowNumber
            None,                           # context
            NX_SUBTYPE_AUX_CONTROL_BUTTONS, # subtype
            data1,                          # data1
            -1,                             # data2
        )

    def _tap_key(self, key: int) -> None:
        ev_down = self._media_key_event(key, True)
        ev_up = self._media_key_event(key, False)
        CGEventPost(kCGHIDEventTap, ev_down.CGEvent())
        time.sleep(0.02)
        CGEventPost(kCGHIDEventTap, ev_up.CGEvent())

    def toggle_play_pause(self) -> None:
        self._tap_key(NX_KEYTYPE_PLAY)

    def toggle_mute(self) -> None:
        self._tap_key(NX_KEYTYPE_MUTE)