# src/aircontrol/main.py

import cv2
import pyautogui

from aircontrol.camera import Camera
from aircontrol.tracking import HandTracker

from aircontrol.cursor.controller import CursorController
from aircontrol.actions.mouse_control import MouseController


def main():
    screen_w, screen_h = pyautogui.size()

    cam = Camera()
    tracker = HandTracker()
    mouse = MouseController()

    cursor = CursorController(
        screen_w=screen_w,
        screen_h=screen_h,
        mode_name="palm",
        enabled=True,
    )

    try:
        while True:
            frame = cam.get_frame()
            hands = tracker.process(frame)

            # --- cursor move ---
            if hands:
                hand_lms = hands[0]["landmarks"]
                pos_xy = cursor.update_xy(hand_lms) 

                if pos_xy is not None:
                    px, py = pos_xy
                    mouse.move_to(px, py)
            else:
                # no hand detected → reset smoothing to avoid jump 
                cursor.smoother.reset()

            cam.show(frame)

            # --- Quit / Toggle options ---
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"): # quit program
                break
            elif key == ord("t"): # turn of cursor movement
                cursor.toggle_enabled()
                print(f"[CURSOR] enabled={cursor.enabled}")
            elif key == ord("m"): # change cursor mode
                cursor.toggle_mode()
                print(f"[CURSOR] mode={cursor.mode_name}")

    finally:
        tracker.close()
        cam.release()


if __name__ == "__main__":
    main()