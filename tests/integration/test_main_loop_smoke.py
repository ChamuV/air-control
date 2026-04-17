# tests/integration/test_main_loop_smoke.py

import sys
from types import SimpleNamespace

from aircontrol.gestures.events import GestureEvent
import aircontrol.main as main_mod


class DummyEngine:
    def __init__(self):
        self.hand_inputs = []

    def update(self, hand_landmarks):
        self.hand_inputs.append(hand_landmarks)
        return [GestureEvent("gesture.pinch", {})]


class DummyDispatcher:
    def __init__(self):
        self.dispatched = []

    def dispatch(self, event):
        self.dispatched.append(event)
        return True


def test_main_runs_one_iteration_and_cleans_up(monkeypatch):
    state = {}

    class DummyCamera:
        def __init__(self):
            self.frame_count = 0
            self.released = False
            state["camera"] = self

        def get_frame(self):
            self.frame_count += 1
            return {"frame": self.frame_count}

        def show(self, frame):
            state["shown_frame"] = frame

        def release(self):
            self.released = True

    class DummyTracker:
        def __init__(self, max_num_hands=1):
            self.max_num_hands = max_num_hands
            self.closed = False
            self.process_calls = 0
            state["tracker"] = self

        def process(self, frame):
            self.process_calls += 1
            return []

        def close(self):
            self.closed = True

    class DummyCursor:
        def __init__(self, **kwargs):
            self.enabled = True
            self.toggle_calls = 0
            state["cursor"] = self

        def toggle_enabled(self):
            self.enabled = not self.enabled
            self.toggle_calls += 1

        def update_xy(self, hand_lms):
            return (100, 200)

    class DummyMouse:
        pass

    class DummyMedia:
        pass

    class DummyScreenshot:
        def __init__(self, out_dir):
            self.out_dir = out_dir

    engine = DummyEngine()
    dispatcher = DummyDispatcher()
    state["engine"] = engine
    state["dispatcher"] = dispatcher

    fake_pyautogui = SimpleNamespace(size=lambda: (1920, 1080))
    monkeypatch.setitem(sys.modules, "pyautogui", fake_pyautogui)

    monkeypatch.setattr(main_mod.cv2, "waitKey", lambda _: ord("q"))
    monkeypatch.setattr(main_mod, "Camera", DummyCamera)
    monkeypatch.setattr(main_mod, "HandTracker", DummyTracker)
    monkeypatch.setattr(main_mod, "CursorController", DummyCursor)
    monkeypatch.setattr(main_mod, "MouseController", DummyMouse)
    monkeypatch.setattr(main_mod, "MediaControllerMacOS", DummyMedia)
    monkeypatch.setattr(main_mod, "CameraScreenshotController", DummyScreenshot)
    monkeypatch.setattr(main_mod, "default_plugins", lambda: [])
    monkeypatch.setattr(main_mod, "build_gesture_system", lambda ctx, plugins: (engine, dispatcher))

    main_mod.main()

    assert state["camera"].frame_count == 1
    assert state["tracker"].process_calls == 1
    assert state["engine"].hand_inputs == [None]
    assert [e.name for e in state["dispatcher"].dispatched] == ["gesture.pinch"]
    assert state["camera"].released is True
    assert state["tracker"].closed is True