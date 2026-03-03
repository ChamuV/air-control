# src/aircontrol/gestures/events.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GestureEvent:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)