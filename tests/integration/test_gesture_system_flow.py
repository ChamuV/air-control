# tests/integration/test_gesture_system_flow.py

from types import SimpleNamespace

from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.loader import build_gesture_system
from aircontrol.gestures.plugin_base import PluginRegistration


class DummyDetector:
    def update(self, hand_landmarks):
        return [GestureEvent("gesture.pinch", {"source": "detector"})]


class DummyPlugin:
    def register(self, ctx):
        def click_action(event: GestureEvent):
            ctx.calls.append(event)

        return PluginRegistration(
            detectors=[DummyDetector()],
            actions={"mouse.click": click_action},
        )


def test_build_gesture_system_end_to_end_maps_and_dispatches():
    ctx = SimpleNamespace(calls=[])
    engine, dispatcher = build_gesture_system(ctx, plugins=[DummyPlugin()])

    events = engine.update(hand_landmarks=object())
    assert [e.name for e in events] == ["gesture.pinch"]

    for event in events:
        dispatched = dispatcher.dispatch(event)
        assert dispatched is True

    assert len(ctx.calls) == 1
    assert ctx.calls[0].name == "mouse.click"
    assert ctx.calls[0].payload["source"] == "detector"
