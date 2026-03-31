# tests/plugins/commands/test_scroll_continuous_command.py

from types import SimpleNamespace

from aircontrol.gestures.events import GestureEvent
from aircontrol.plugins.commands.scroll_continuous import ScrollContinuousCommandPlugin


class DummyMouse:
    def __init__(self):
        self.calls = []

    def scroll(self, clicks):
        self.calls.append(int(clicks))


def test_scroll_continuous_defaults_to_positive_one():
    ctx = SimpleNamespace(mouse=DummyMouse())
    plugin = ScrollContinuousCommandPlugin()
    registration = plugin.register(ctx)

    registration.actions["scroll.continuous"](GestureEvent("scroll.continuous", {}))

    assert ctx.mouse.calls == [1]


def test_scroll_continuous_direction_down_inverts_sign():
    ctx = SimpleNamespace(mouse=DummyMouse())
    plugin = ScrollContinuousCommandPlugin()
    registration = plugin.register(ctx)

    registration.actions["scroll.continuous"](
        GestureEvent("scroll.continuous", {"direction": "down", "amount": 7})
    )

    assert ctx.mouse.calls == [-7]
