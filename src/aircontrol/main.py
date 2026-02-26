# src/aircontrol/main.py

import cv2
import pyautogui 

from aircontrol.camera import Camera
from aircontrol.tracking import HandTracker

from aircontrol.gestures.features import center_of_mass
from aircontrol.gestures.pinch import PinchDetector
from aircontrol.gestures.volume_gesture import VolumeGesture

from aircontrol.actions.mouse_control import MouseController
from aircontrol.actions.volume_control import VolumeController


def main():
    cam = Camera()
    tracker = HandTracker(max_num_hands=1)
    mouse = MouseController()

    pinch = PinchDetector(threshold=0.04)

    vol = VolumeController(step=4) # each "step" is 4 volume points on macOS
    vol_gesture = VolumeGesture(ticks_per_sec=10)


    try:
        while True:
            frame = cam.get_frame()

            hands = tracker.process(frame)
            
            ###DEBUG
            #print(len(hands))

            if hands:
                hand_lms = hands[0]["landmarks"]
                norm_pt, _ = center_of_mass(hand_lms)
                mouse.move_to_norm(norm_pt.x, norm_pt.y)

                if pinch.detect(hand_lms):
                    pyautogui.click()

                sig = vol_gesture.update(hand_lms)
                if sig:
                    print(f"[VOL DEBUG] direction={sig.direction}, steps={sig.steps}")
                if sig:
                    if sig.direction == "up":
                        vol.volume_up(sig.steps)
                    else:
                        vol.volume_down(sig.steps)


            cam.show(frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        tracker.close()
        cam.release()

if __name__ == "__main__":
    main()