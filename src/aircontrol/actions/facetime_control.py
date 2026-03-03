# src/aircontrol/actions/facetime_control.py

from __future__ import annotations

import subprocess


class FaceTimeControllerMacOS:
    """
    Initiates a FaceTime call using a phone number.

    Best practice: use E.164 format with country code, e.g. "+919845103831".

    Uses:
        open location "tel:+919845103831"

    Requires:
        - FaceTime installed
        - Accessibility permission for the app running Python (Terminal/VSCode/etc)
          System Settings -> Privacy & Security -> Accessibility
    """

    def __init__(self, phone_number_str: str = "+919845103831"):
        self.phone_number = str(phone_number_str)

    def call(self) -> None:
        script = f'''
        tell application "FaceTime"
            activate
            open location "tel:{self.phone_number}"
            delay 1.5
            tell application "System Events" to key code 36
        end tell
        '''
        subprocess.run(["osascript", "-e", script], check=False)