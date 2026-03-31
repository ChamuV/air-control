# tests/cursor/test_controller.py

from aircontrol.cursor.controller import CursorController


def make_controller(**kwargs):
    controller = CursorController(screen_w=1000, screen_h=800, **kwargs)

    # Keep cursor math deterministic for tests.
    controller.smoother.alpha = 1.0

    class DummyMode:
        def __init__(self):
            self.point = None

        def get_point(self, hand_landmarks):
            return self.point

    dummy_mode = DummyMode()
    controller.index_mode = dummy_mode
    controller.palm_mode = dummy_mode
    return controller, dummy_mode


def test_toggle_mode_flips_and_resets():
    controller, _ = make_controller(mode_name="index")

    initial_mode = controller.mode_name

    controller.toggle_mode()

    assert controller.mode_name != initial_mode
    assert controller.smoother.initialized is False


def test_toggle_enabled_disables_output():
    controller, mode = make_controller(enabled=True)
    mode.point = (0.5, 0.5)

    controller.toggle_enabled()  # disable

    pos = controller.update_xy(object())
    assert pos is None


def test_update_none_resets_state():
    controller, mode = make_controller()
    mode.point = (0.5, 0.5)

    controller.update_xy(object())
    assert controller.smoother.initialized is True

    controller.update_xy(None)

    assert controller.smoother.initialized is False


def test_deadzone_returns_last_output():
    controller, mode = make_controller(deadzone_px=10)
    mode.point = (0.5, 0.5)
    first = controller.update_xy(object())

    mode.point = (0.501, 0.501)  # tiny move
    second = controller.update_xy(object())

    assert first == second


def test_gain_reduces_jump_size():
    controller_fast, mode_fast = make_controller(gain=1.0, deadzone_px=0)
    mode_fast.point = (0.2, 0.2)
    p1_fast = controller_fast.update_xy(object())
    mode_fast.point = (0.8, 0.8)
    p2_fast = controller_fast.update_xy(object())

    controller_slow, mode_slow = make_controller(gain=0.2, deadzone_px=0)
    mode_slow.point = (0.2, 0.2)
    p1_slow = controller_slow.update_xy(object())
    mode_slow.point = (0.8, 0.8)
    p2_slow = controller_slow.update_xy(object())

    jump_fast = abs(p2_fast[0] - p1_fast[0]) + abs(p2_fast[1] - p1_fast[1])
    jump_slow = abs(p2_slow[0] - p1_slow[0]) + abs(p2_slow[1] - p1_slow[1])
    assert jump_slow < jump_fast


def test_clamping_keeps_coordinates_in_bounds():
    controller, mode = make_controller(edge_padding_px=3, deadzone_px=0)
    mode.point = (10.0, 10.0)  # extreme normalized point, mode could return bad values

    x, y = controller.update_xy(object())

    assert 3 <= x <= 996
    assert 3 <= y <= 796
