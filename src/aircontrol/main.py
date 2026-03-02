# src/aircontrol/main.py

import cv2
import pyautogui

from aircontrol.camera import Camera
from aircontrol.tracking import HandTracker

from aircontrol.gestures.features import center_of_mass
from aircontrol.gestures.pinch import PinchDetector
from aircontrol.gestures.volume_gesture import VolumeMotionGesture
from aircontrol.gestures.window_gesture import WindowMotionGesture

from aircontrol.actions.mouse_control import MouseController
from aircontrol.actions.volume_control import VolumeControllerMacOS
from aircontrol.actions.window_control import WindowControllerMacOS


def main():
    cam = Camera()
    tracker = HandTracker(max_num_hands=1)
    mouse = MouseController()

    pinch = PinchDetector(threshold=0.04)

    # -------- Volume Gesture --------
    vol_gesture = VolumeMotionGesture(
        pinky_y_spread_thresh=0.03,
        speed_thresh=0.10,
        consensus_frac=0.8,
        tick_dt=0.15,
        gain=10.0,
        max_steps_per_tick=4,
    )
    volume = VolumeControllerMacOS(delta_per_step=4)

    # -------- Window Gesture --------
    window_gesture = WindowMotionGesture(
        tip_x_spread_thresh=0.05,
        min_extension_x=0.03,
        swipe_dist_thresh=0.10,
        tick_dt=0.40,
    )
    window = WindowControllerMacOS()

    try:
        while True:
            frame = cam.get_frame()
            hands = tracker.process(frame)

            if hands:
                hand_lms = hands[0]["landmarks"]

                # Volume Gesture Check
                vol_signal, vol_dbg = vol_gesture.update(hand_lms)

                if vol_dbg["horizontal_ok"]:
                    if vol_signal:
                        print(f"[VOL] {vol_signal.direction} steps={vol_signal.steps}")
                        try:
                            volume.change(vol_signal.direction, vol_signal.steps)
                        except Exception as e:
                            print("[VOL ERROR]", e)

                else:
                    # Window Gesture Check
                    win_signal, win_dbg = window_gesture.update(hand_lms)

                    if win_signal:
                        print(
                            f"[WINDOW] {win_signal.direction} "
                            f"dx={win_dbg['dx']:.3f} spread={win_dbg['tips_spread']:.3f}"
                        )
                        try:
                            if win_signal.direction == "right":
                                window.switch_right()
                            else:
                                window.switch_left()
                        except Exception as e:
                            print("[WINDOW ERROR]", e)

                    else:
                        # Mouse + Pinch
                        norm_pt, _ = center_of_mass(hand_lms)
                        mouse.move_to_norm(norm_pt.x, norm_pt.y)

                        if pinch.detect(hand_lms):
                            print("[PINCH CLICK]")
                            pyautogui.click()

            cam.show(frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        tracker.close()
        cam.release()


if __name__ == "__main__":
    main()