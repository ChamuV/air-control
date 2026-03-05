# src/aircontrol/gestures/mapper.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass(frozen=True)
class Binding:
    gesture: str
    action: str
    state: str = "any"
    params: Dict[str, Any] | None = None


class GestureMapper:
    def __init__(self, config_path: str):
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Gesture map YAML not found: {path}")

        with open(path, "r") as f:
            cfg = yaml.safe_load(f) or {}

        self.profile: str = str(cfg.get("profile", "default"))
        self._bindings: Dict[str, Binding] = {}

        for b in cfg.get("bindings", []):
            gesture = str(b["gesture"])
            action = str(b["action"])
            state = str(b.get("state", "any"))
            params = b.get("params", None)

            if params is not None and not isinstance(params, dict):
                raise TypeError(f"params must be a mapping for {gesture}, got {type(params)}")

            self._bindings[gesture] = Binding(
                gesture=gesture,
                action=action,
                state=state,
                params=params,
            )

    def resolve(self, gesture_name: str, state: str = "any") -> Optional[Binding]:
        b = self._bindings.get(gesture_name)
        if b is None:
            return None

        # simple state filter
        if b.state != "any" and b.state != state:
            return None

        return b