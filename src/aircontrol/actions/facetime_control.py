# src/aircontrol/actions/facetime_control.py

from __future__ import annotations

import subprocess


class FaceTimeControllerMacOS:
    """
    Start a FaceTime call.

    Modes:
        video -> facetime://
        audio -> facetime-audio://

    Example number format:
        "+919845103831"

    Requires:
        FaceTime installed
        Accessibility permission for Python host
    """

    def __init__(self, phone_number_str: str = "+919845103831", mode: str = "video"):
        self.phone_number = str(phone_number_str)
        self.mode = mode

    def _call_url(self) -> str:
        if self.mode == "video":
            return f"facetime://{self.phone_number}"
        return f"facetime-audio://{self.phone_number}"

    def call(self) -> None:
        url = self._call_url()

        script = f'''
        tell application "FaceTime"
            activate
            open location "{url}"
        end tell

        delay 0.4

        tell application "System Events"
            key code 36
        end tell
        '''

        subprocess.run(["osascript", "-e", script], check=False)