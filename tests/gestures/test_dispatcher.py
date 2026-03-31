# tests/gestures/test_dispatcher.py

from aircontrol.gestures.dispatcher import GestureDispatcher
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.mapper import Binding


class DummyMapper:
    def __init__(self, binding=None):
        self.binding = binding

    def resolve(self, gesture_name: str, state: str = "any"):
        return self.binding


def test_dispatcher_executes_action_event_directly():
    called = {"ran": False}

    def handler(event):
        called["ran"] = True

    # Current dispatcher requires mapper to be set; for non-gesture events
    # the mapper is not consulted, but it must exist.
    dispatcher = GestureDispatcher(mapper=DummyMapper())
    dispatcher.register("mouse.click", handler)

    result = dispatcher.dispatch(GestureEvent("mouse.click"))

    assert result is True
    assert called["ran"] is True


def test_dispatcher_maps_gesture_to_action():
    called = {"ran": False}

    def handler(event):
        called["ran"] = True

    mapper = DummyMapper(
        binding=Binding(
            gesture="gesture.pinch",
            state="any",
            action="mouse.click",
            params=None,
        )
    )
    dispatcher = GestureDispatcher(mapper=mapper)
    dispatcher.register("mouse.click", handler)

    result = dispatcher.dispatch(GestureEvent("gesture.pinch"))

    assert result is True
    assert called["ran"] is True


def test_dispatcher_merges_event_payload_with_params():
    captured = {}

    def handler(event):
        captured["payload"] = event.payload

    mapper = DummyMapper(
        binding=Binding(
            gesture="gesture.scroll",
            state="any",
            action="scroll.continuous",
            params={"amount": 10},
        )
    )
    dispatcher = GestureDispatcher(mapper=mapper)
    dispatcher.register("scroll.continuous", handler)

    dispatcher.dispatch(GestureEvent("gesture.scroll", payload={"direction": "down"}))

    payload = captured["payload"]
    assert payload["direction"] == "down"
    assert payload["amount"] == 10


def test_dispatcher_returns_false_when_no_mapper_or_handler():
    dispatcher = GestureDispatcher(mapper=None)
    result = dispatcher.dispatch(GestureEvent("gesture.unknown"))
    assert result is False


def test_dispatcher_returns_false_when_no_binding_found():
    mapper = DummyMapper(binding=None)
    dispatcher = GestureDispatcher(mapper=mapper)
    dispatcher.register("mouse.click", lambda e: None)
    result = dispatcher.dispatch(GestureEvent("gesture.pinch"))
    assert result is False
