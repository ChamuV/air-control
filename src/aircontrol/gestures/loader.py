# src/aircontrol/gestures/loader.py

from __future__ import annotations

from typing import Any, Iterable
from pathlib import Path

from .engine import GestureEngine
from .dispatcher import GestureDispatcher
from .plugin_base import GesturePlugin
from .mapper import GestureMapper


def build_gesture_system(ctx: Any, plugins: Iterable[GesturePlugin]):
    all_detectors = []

    # Load gesture->action bindings from YAML
    config_path = Path(__file__).resolve().parents[1] / "config" / "gesture_map.yaml"
    mapper = GestureMapper(str(config_path))

    dispatcher = GestureDispatcher(mapper=mapper)

    for plugin in plugins:
        reg = plugin.register(ctx)

        # detectors (gesture emitters)
        all_detectors.extend(reg.detectors)

        # actions (command handlers)
        for action_name, action in reg.actions.items():
            dispatcher.register(action_name, action)

    engine = GestureEngine(all_detectors)
    return engine, dispatcher