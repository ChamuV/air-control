# src/aircontrol/plugins/discovery.py

from __future__ import annotations

import importlib
import pkgutil
from typing import List

import aircontrol.plugins
import aircontrol.plugins.detectors
import aircontrol.plugins.commands


def _discover_from_package(pkg) -> List[object]:
    discovered: List[object] = []

    package_path = pkg.__path__
    package_name = pkg.__name__

    for module_info in pkgutil.iter_modules(package_path):
        module_name = module_info.name

        # Skip private or helper modules
        if module_name.startswith("_"):
            continue
        if module_name in {"discovery"}:
            continue

        full_module_name = f"{package_name}.{module_name}"

        try:
            module = importlib.import_module(full_module_name)
        except Exception as e:
            print(f"[PLUGIN LOAD ERROR] {full_module_name}: {e}")
            continue

        plugin_factory = getattr(module, "plugin", None)
        if not callable(plugin_factory):
            continue

        try:
            plugin_instance = plugin_factory()
            discovered.append(plugin_instance)
            print(f"[PLUGIN LOADED] {full_module_name}")
        except Exception as e:
            print(f"[PLUGIN INIT ERROR] {full_module_name}: {e}")

    return discovered


def discover_plugins() -> List[object]:
    """
    Auto-discover plugins inside:
      - aircontrol.plugins.detectors
      - aircontrol.plugins.commands

    A plugin module must expose:
        def plugin() -> object
    """
    discovered: List[object] = []

    discovered.extend(_discover_from_package(aircontrol.plugins.detectors))
    discovered.extend(_discover_from_package(aircontrol.plugins.commands))

    return discovered