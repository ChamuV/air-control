# test.py

from AppKit import NSEvent
from Quartz import CGEventPost, kCGHIDEventTap
import time

NX_SYSDEFINED = 14
NX_SUBTYPE_AUX_CONTROL_BUTTONS = 8
NX_KEYTYPE_PLAY = 16  # Play/Pause

def media_key_event(key: int, key_down: bool):
    flags = 0xA00
    if key_down:
        data1 = (key << 16) | flags
    else:
        data1 = (key << 16) | (flags | 0x100)

    # IMPORTANT: exactly 9 args here
    return NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
        NX_SYSDEFINED,            # type
        (0, 0),                  # location
        0,                       # modifierFlags
        0.0,                     # timestamp
        0,                       # windowNumber
        None,                    # context
        NX_SUBTYPE_AUX_CONTROL_BUTTONS,  # subtype
        data1,                   # data1
        -1,                      # data2
    )

def press_play_pause():
    ev_down = media_key_event(NX_KEYTYPE_PLAY, True)
    ev_up   = media_key_event(NX_KEYTYPE_PLAY, False)

    CGEventPost(kCGHIDEventTap, ev_down.CGEvent())
    time.sleep(0.02)
    CGEventPost(kCGHIDEventTap, ev_up.CGEvent())

if __name__ == "__main__":
    print("Starting in 3 seconds...")
    time.sleep(3)
    print("Pausing...")
    press_play_pause()
    time.sleep(2)
    print("Playing again...")
    press_play_pause()
    print("Done.")