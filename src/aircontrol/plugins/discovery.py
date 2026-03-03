# src/aircontrol/plugins/discovery.py

from __future__ import annotations

import importlib
import pkgutil
from typing import List

import aircontrol.plugins  # important: gives us __path__


def discover_plugins() -> List[object]:
    """
    Auto-discover plugins inside aircontrol.plugins package.

    A plugin module must expose:

        def plugin() -> GesturePlugin

    Returns:
        List of instantiated plugin objects.
    """
    discovered = []

    package_path = aircontrol.plugins.__path__
    package_name = aircontrol.plugins.__name__

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

        # Look for factory function
        plugin_factory = getattr(module, "plugin", None)

        if callable(plugin_factory):
            try:
                plugin_instance = plugin_factory()
                discovered.append(plugin_instance)
                print(f"[PLUGIN LOADED] {module_name}")
            except Exception as e:
                print(f"[PLUGIN INIT ERROR] {module_name}: {e}")

    return discovered