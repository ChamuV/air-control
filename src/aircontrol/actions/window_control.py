# scr/aircontrol/actions/window_control.py

import subprocess

class WindowControllerMacOS:
    """
    Uses AppleScript to simulate Cmd+Tab window/app switching.
    """

    def switch_right(self):
        # Cmd + Tab
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to key code 48 using command down']
        )

    def switch_left(self):
        # Cmd + Shift + Tab
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to key code 48 using {command down, shift down}']
        )