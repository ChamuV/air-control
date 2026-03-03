# src/aircontrol/app_context.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .actions.mouse_control import MouseController
from .actions.media_control import MediaControllerMacOS
from .actions.facetime_control import FaceTimeControllerMacOS
from .actions.camera_screenshot_control import CameraScreenshotController


from .cursor.controller import CursorController

@dataclass
class AppContext:
    mouse: MouseController
    cursor: CursorController
    media: MediaControllerMacOS

    facetime: FaceTimeControllerMacOS
    camera_screenshot: CameraScreenshotController

    latest_frame: Optional[Any] = None