# src/aircontrol/main.py

import cv2
import pyautogui 

from aircontrol.camera import Camera
from aircontrol.tracking import HandTracker

from aircontrol.gestures.features import center_of_mass
from aircontrol.gestures.pinch import PinchDetector
from aircontrol.gestures.volume_gesture import VolumeMotionGesture

from aircontrol.actions.mouse_control import MouseController
from aircontrol.actions.volume_control import VolumeControllerMacOS


def main():
    cam = Camera()
    tracker = HandTracker(max_num_hands=1)
    mouse = MouseController()

    pinch = PinchDetector(threshold=0.04)

    vol_gesture = VolumeMotionGesture(
    pinky_y_spread_thresh=0.03,
    speed_thresh=0.1,
    consensus_frac=0.8,
    tick_dt=0.15,
    gain=10.0,
    max_steps_per_tick=4,
    )

    volume = VolumeControllerMacOS(delta_per_step=4)


    try:
        while True:
            frame = cam.get_frame()

            hands = tracker.process(frame)
            
            ###DEBUG
            #print(len(hands))

            #if hands:
            #    hand_lms = hands[0]["landmarks"]
            #    norm_pt, _ = center_of_mass(hand_lms)
            #    mouse.move_to_norm(norm_pt.x, norm_pt.y)
#
            #    if pinch.detect(hand_lms):
            #        pyautogui.click()
#
            #    signal, dbg = vol_gesture.update(hand_lms)
            #    if signal:
            #        try:
            #            new_v = volume.change(signal.direction, signal.steps)
            #        except Exception as e:
            #            print("[VOL ERROR]", e)

            if hands:
                hand_lms = hands[0]["landmarks"]

                signal, dbg = vol_gesture.update(hand_lms)

                if dbg["horizontal_ok"]:
                    # volume only
                    if signal:
                        try:
                            volume.change(signal.direction, signal.steps)
                        except Exception as e:
                            print("[VOL ERROR]", e)
                else:
                    # mouse + pinch only
                    norm_pt, _ = center_of_mass(hand_lms)
                    mouse.move_to_norm(norm_pt.x, norm_pt.y)

                    if pinch.detect(hand_lms):
                        pyautogui.click()
                
            cam.show(frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        tracker.close()
        cam.release()

if __name__ == "__main__":
    main()