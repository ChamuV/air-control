# src/aircontrol/main.py

from __future__ import annotations

import cv2
import pyautogui

from aircontrol.camera import Camera
from aircontrol.tracking import HandTracker
from aircontrol.cursor.controller import CursorController

from aircontrol.actions.mouse_control import MouseController
from aircontrol.actions.media_control import MediaControllerMacOS
from aircontrol.actions.camera_screenshot_control import CameraScreenshotController

from aircontrol.app_context import AppContext
from aircontrol.gestures.events import GestureEvent
from aircontrol.gestures.loader import build_gesture_system
from aircontrol.plugins import default_plugins

from aircontrol.ui.gesture_hud import draw_gesture_hud


def main() -> None:
    screen_w, screen_h = pyautogui.size()

    cam = Camera()
    tracker = HandTracker(max_num_hands=1)

    mouse = MouseController()
    media = MediaControllerMacOS()
    camera_screenshot = CameraScreenshotController(out_dir="captures")

    cursor = CursorController(
        screen_w=screen_w,
        screen_h=screen_h,
        mode_name="index",
        enabled=True,
    )

    ctx = AppContext(
        mouse=mouse,
        cursor=cursor,
        media=media,
        camera_screenshot=camera_screenshot,
    )

    plugins = default_plugins()
    engine, dispatcher = build_gesture_system(ctx, plugins)

    try:
        while True:
            frame = cam.get_frame()
            ctx.latest_frame = frame

            hands = tracker.process(frame)
            hand_lms = hands[0]["landmarks"] if hands else None

            events = engine.update(hand_lms)

            # continuous cursor motion
            if hand_lms is not None and cursor.enabled:
                pos = cursor.update_xy(hand_lms)
                if pos is not None:
                    px, py = pos
                    events.append(GestureEvent("cursor.move", {"x": px, "y": py}))

            for event in events:
                dispatcher.dispatch(event)

            # test HUD
            draw_gesture_hud(frame, label="Call Sign", progress=0.5)

            cam.show(frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("t"):
                cursor.toggle_enabled()
                print(f"[CURSOR] enabled={cursor.enabled}")

    finally:
        tracker.close()
        cam.release()


if __name__ == "__main__":
    main()