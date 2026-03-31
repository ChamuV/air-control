# tests/plugins/commands/test_media_commands.py

from types import SimpleNamespace

from aircontrol.gestures.events import GestureEvent
from aircontrol.plugins.commands.media_mute_toggle import MediaMuteToggleCommandPlugin
from aircontrol.plugins.commands.media_play_pause import MediaPlayPauseCommandPlugin
from aircontrol.plugins.commands.media_volume_up import MediaVolumeUpCommandPlugin
from aircontrol.plugins.commands.media_volume_down import MediaVolumeDownCommandPlugin


class DummyMedia:
    def __init__(self):
        self.calls = []

    def toggle_mute(self):
        self.calls.append(("toggle_mute",))

    def toggle_play_pause(self):
        self.calls.append(("toggle_play_pause",))

    def volume_up(self, steps):
        self.calls.append(("volume_up", steps))

    def volume_down(self, steps):
        self.calls.append(("volume_down", steps))


def test_mute_action_invokes_ctx_media_method():
    ctx = SimpleNamespace(media=DummyMedia())

    plugin = MediaMuteToggleCommandPlugin()
    registration = plugin.register(ctx)

    handler = registration.actions["media.mute_toggle"]
    handler(GestureEvent("media.mute_toggle"))

    assert ctx.media.calls == [("toggle_mute",)]


def test_play_pause_action_invokes_ctx_media_method():
    ctx = SimpleNamespace(media=DummyMedia())

    plugin = MediaPlayPauseCommandPlugin()
    registration = plugin.register(ctx)

    handler = registration.actions["media.play_pause"]
    handler(GestureEvent("media.play_pause"))

    assert ctx.media.calls == [("toggle_play_pause",)]


def test_volume_up_action_invokes_ctx_media_method():
    ctx = SimpleNamespace(media=DummyMedia())

    plugin = MediaVolumeUpCommandPlugin()
    registration = plugin.register(ctx)

    handler = registration.actions["media.volume_up"]
    handler(GestureEvent("media.volume_up"))

    assert ctx.media.calls == [("volume_up", 1)]


def test_volume_down_action_invokes_ctx_media_method():
    ctx = SimpleNamespace(media=DummyMedia())

    plugin = MediaVolumeDownCommandPlugin()
    registration = plugin.register(ctx)

    handler = registration.actions["media.volume_down"]
    handler(GestureEvent("media.volume_down"))

    assert ctx.media.calls == [("volume_down", 1)]
