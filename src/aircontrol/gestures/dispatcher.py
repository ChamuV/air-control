# src/aircontrol/gestures/dispatcher.py

from __future__ import annotations

from typing import Callable, Optional, Any

from .events import GestureEvent
from .mapper import GestureMapper, Binding

Action = Callable[[GestureEvent], None]


class GestureDispatcher:
    def __init__(self, mapper: Optional[GestureMapper] = None) -> None:
        # map action name -> action function
        self._actions: dict[str, Action] = {}
        self._mapper = mapper

    def register(self, action_name: str, action: Action) -> None:
        """
        Register/overwrite an action for an action name (e.g. "mouse.click").
        """
        self._actions[action_name] = action

    def set_mapper(self, mapper: GestureMapper) -> None:
        self._mapper = mapper

    def _map_gesture_to_action_event(self, event: GestureEvent) -> Optional[GestureEvent]:
        """
        If this is a gesture event (gesture.*) and a mapper exists, map it to an action event.
        Returns:
            - mapped action GestureEvent if mapping exists
            - None if mapping does not exist
        """
        if self._mapper is None:
            return None

        if not event.name.startswith("gesture."):
            return event  # already an action event

        binding: Optional[Binding] = self._mapper.resolve(event.name, state="any")
        if binding is None:
            return None

        payload: dict[str, Any] = {}
        payload.update(event.payload or {})
        payload.update(binding.params or {})

        return GestureEvent(binding.action, payload)

    def dispatch(self, event: GestureEvent) -> bool:
        """
        Dispatch a GestureEvent.

        Behavior:
          - If event is gesture.*: map via YAML to an action event.
          - Then execute action handler if registered.

        Returns:
            True if an action was found and executed.
            False otherwise.
        """
        mapped = self._map_gesture_to_action_event(event)
        if mapped is None:
            return False

        action = self._actions.get(mapped.name)
        if action is None:
            return False

        action(mapped)
        return True

    def has_action(self, action_name: str) -> bool:
        return action_name in self._actions