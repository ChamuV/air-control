# src/aircontrol/main.py

import cv2
import pyautogui

from aircontrol.camera import Camera
from aircontrol.tracking import HandTracker

from aircontrol.cursor.controller import CursorController

from aircontrol.actions.mouse_control import MouseController
from aircontrol.actions.media_control import MediaControllerMacOS

from aircontrol.app_context import AppContext

from aircontrol.gestures.loader import build_gesture_system

from aircontrol.plugins import default_plugins


def main():
    screen_w, screen_h = pyautogui.size()

    cam = Camera()
    tracker = HandTracker(max_num_hands=1)
    mouse = MouseController()
    media = MediaControllerMacOS()

    cursor = CursorController(
        screen_w=screen_w,
        screen_h=screen_h,
        mode_name="palm",
        enabled=True,
    )

    ctx = AppContext(mouse=mouse, cursor=cursor, media=media)

    plugins = default_plugins()
    engine, dispatcher = build_gesture_system(ctx, plugins)

    try:
        while True:
            frame = cam.get_frame()
            hands = tracker.process(frame)

            hand_lms = hands[0]["landmarks"] if hands else None

            # --- run gesture system ---
            events = engine.update(hand_lms)
            for event in events:
                dispatcher.dispatch(event)
                print(event.name)

            cam.show(frame)

            # --- Quit / Toggle options ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):  # quit program
                break
            elif key == ord("t"):  # toggle cursor movement
                cursor.toggle_enabled()
                print(f"[CURSOR] enabled={cursor.enabled}")
            elif key == ord("m"):  # change cursor mode
                cursor.toggle_mode()
                print(f"[CURSOR] mode={cursor.mode_name}")

    finally:
        tracker.close()
        cam.release()


if __name__ == "__main__":
    main()