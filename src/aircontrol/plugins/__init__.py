# src/aircontrol/plugins/__init__.py

from __future__ import annotations

from .discovery import discover_plugins

def default_plugins():
    return discover_plugins()