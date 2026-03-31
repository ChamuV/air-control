# tests/gestures/test_mapper.py

from pathlib import Path

import pytest

from aircontrol.gestures.mapper import GestureMapper


def make_mapper(tmp_path: Path, yaml_body: str) -> GestureMapper:
    path = tmp_path / "gesture_map.yaml"
    path.write_text(yaml_body.strip())
    return GestureMapper(str(path))


def test_mapper_resolves_known_gesture(tmp_path: Path):
    mapper = make_mapper(
        tmp_path,
        """
profile: default

bindings:
  - gesture: gesture.pinch
    state: any
    action: mouse.click
""",
    )

    binding = mapper.resolve("gesture.pinch", state="any")

    assert binding is not None
    assert binding.action == "mouse.click"
    assert binding.gesture == "gesture.pinch"
    assert binding.state == "any"


def test_mapper_returns_none_for_unknown_gesture(tmp_path: Path):
    mapper = make_mapper(
        tmp_path,
        """
profile: default

bindings:
  - gesture: gesture.pinch
    state: any
    action: mouse.click
""",
    )

    assert mapper.resolve("gesture.unknown", state="any") is None


def test_mapper_requires_params_to_be_dict(tmp_path: Path):
    with pytest.raises(TypeError):
        make_mapper(
            tmp_path,
            """
profile: default

bindings:
  - gesture: gesture.call_sign
    state: any
    action: call.start
    params: hello
""",
        )


def test_mapper_allows_any_state(tmp_path: Path):
    mapper = make_mapper(
        tmp_path,
        """
profile: default

bindings:
  - gesture: gesture.pinch
    state: any
    action: mouse.click
""",
    )

    binding = mapper.resolve("gesture.pinch", state="start")

    assert binding is not None
    assert binding.action == "mouse.click"


def test_mapper_matches_specific_state(tmp_path: Path):
    mapper = make_mapper(
        tmp_path,
        """
profile: default

bindings:
  - gesture: gesture.ring_pinch
    state: start
    action: drag.start
""",
    )

    binding = mapper.resolve("gesture.ring_pinch", state="start")

    assert binding is not None
    assert binding.action == "drag.start"


def test_mapper_rejects_state_mismatch(tmp_path: Path):
    mapper = make_mapper(
        tmp_path,
        """
profile: default

bindings:
  - gesture: gesture.ring_pinch
    state: start
    action: drag.start
""",
    )

    assert mapper.resolve("gesture.ring_pinch", state="move") is None
