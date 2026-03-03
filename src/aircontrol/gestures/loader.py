# src/aircontrol/gestures/loader.py

from __future__ import annotations

from typing import Any, Iterable

from .engine import GestureEngine
from .dispatcher import GestureDispatcher
from .plugin_base import GesturePlugin 

def build_gesture_system(ctx: Any, plugins: Iterable[GesturePlugin]):
    all_detectors = []
    
    dispatcher = GestureDispatcher()
    
    for plugin in plugins:
        reg = plugin.register(ctx)
        
        # detectors
        all_detectors.extend(reg.detectors)

        # actions
        for gesture_name, action in reg.actions.items():
            dispatcher.register(gesture_name, action)

    engine = GestureEngine(all_detectors)
    return engine, dispatcher