# tests/integration/test_gesture_map_coverage.py

from pathlib import Path
from types import SimpleNamespace

import yaml

from aircontrol.gestures.loader import build_gesture_system
from aircontrol.plugins import default_plugins


def test_all_gesture_map_actions_have_registered_handlers():
    plugins = default_plugins()
    _, dispatcher = build_gesture_system(SimpleNamespace(), plugins)

    repo_root = Path(__file__).resolve().parents[2]
    map_path = repo_root / "src" / "aircontrol" / "config" / "gesture_map.yaml"
    cfg = yaml.safe_load(map_path.read_text()) or {}

    actions = {binding["action"] for binding in cfg.get("bindings", [])}
    missing = [action for action in sorted(actions) if not dispatcher.has_action(action)]

    assert missing == [], f"Missing action handlers for mapped actions: {missing}"
