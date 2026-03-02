# src/aircontrol/actions/window_control.py

import subprocess


class WindowControllerMacOS:
    """
    macOS window/app switching via Cmd+Tab and Cmd+Shift+Tab using AppleScript.

    Note: This requires Accessibility permission for Terminal/Python:
      System Settings → Privacy & Security → Accessibility
    """

    def _run(self, script: str) -> None:
        p = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
        if p.returncode != 0:
            raise RuntimeError(p.stderr.strip() or p.stdout.strip())

    def switch_right(self) -> None:
        # Next window/app to the RIGHT (Cmd + Tab)
        self._run('tell application "System Events" to keystroke tab using command down')

    def switch_left(self) -> None:
        # Next window/app to the LEFT (Cmd + Shift + Tab)
        self._run('tell application "System Events" to keystroke tab using {command down, shift down}')