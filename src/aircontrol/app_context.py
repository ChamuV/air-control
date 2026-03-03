# src/aircontrol/app_context.py

from __future__ import annotations

from dataclasses import dataclass

from .actions.mouse_control import MouseController
from .actions.media_control import MediaControllerMacOS

from .cursor.controller import CursorController

@dataclass
class AppContext:
    mouse: MouseController
    cursor: CursorController
    media: MediaControllerMacOS