# tests/plugins/commands/test_cursor_commands.py

from types import SimpleNamespace

from aircontrol.gestures.events import GestureEvent
from aircontrol.plugins.commands.cursor_move import CursorMoveCommandPlugin
from aircontrol.plugins.commands.cursor_toggle_mode import CursorToggleModeCommandPlugin


class DummyMouse:
    def __init__(self):
        self.calls = []

    def move_to(self, x, y):
        self.calls.append((x, y))


class DummyCursor:
    def __init__(self):
        self.toggle_mode_calls = 0

    def toggle_mode(self):
        self.toggle_mode_calls += 1


def test_cursor_move_calls_ctx_mouse_move_to():
    ctx = SimpleNamespace(
        mouse=DummyMouse(),
        cursor=DummyCursor(),
    )

    plugin = CursorMoveCommandPlugin()
    registration = plugin.register(ctx)

    handler = registration.actions["cursor.move"]
    handler(GestureEvent("cursor.move", payload={"x": 100, "y": 200}))

    assert ctx.mouse.calls == [(100, 200)]


def test_cursor_toggle_mode_calls_ctx_cursor_toggle_mode():
    ctx = SimpleNamespace(
        mouse=DummyMouse(),
        cursor=DummyCursor(),
    )

    plugin = CursorToggleModeCommandPlugin()
    registration = plugin.register(ctx)

    handler = registration.actions["cursor.toggle_mode"]
    handler(GestureEvent("cursor.toggle_mode"))

    assert ctx.cursor.toggle_mode_calls == 1
