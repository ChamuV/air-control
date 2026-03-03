# src/aircontrol/gestures/plugin_base.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .dispatcher import Action
from .events import GestureEvent


class GestureDetector(Protocol):
    def update(self, hand_landmarks) -> list[GestureEvent]:
        """
        Called every frame.

        Args:
            hand_landmarks: MediaPipe hand landmarks object, or None.

        Returns:
            A list of GestureEvent objects (empty list if nothing detected).
        """
        ...


@dataclass
class PluginRegistration:
    detectors: list[GestureDetector]
    actions: dict[str, Action]


class GesturePlugin(Protocol):
    def register(self, ctx: Any) -> PluginRegistration:
        """
        Called once at startup to register this plugin.

        Args:
            ctx: AppContext-like object containing controllers (cursor, mouse, etc.)

        Returns:
            PluginRegistration with:
              - detectors to run each frame
              - actions mapping gesture name -> Action
        """
        ...