# src/aircontrol/gestures/dispatcher.py

from __future__ import annotations

from typing import Callable

from .events import GestureEvent

Action = Callable[[GestureEvent], None]


class GestureDispatcher:
    def __init__(self) -> None:
        # map gesture name -> action
        self._actions: dict[str, Action] = {}

    def register(self, gesture: str, action: Action) -> None:
        """
        Register/overwrite an action for a gesture name.
        """
        self._actions[gesture] = action

    def dispatch(self, event: GestureEvent) -> bool:
        """
        Dispatch a GestureEvent to its registered action.

        Returns:
            True if an action was found and executed.
            False if no action is registered.
        """
        action = self._actions.get(event.name)
        if action is None:
            return False

        action(event)
        return True

    def has_action(self, gesture: str) -> bool:
        """
        Check if a gesture has a registered action.
        """
        return gesture in self._actions