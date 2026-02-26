# volume_gesture_test.py
# Horizontal hand rule: pinky landmarks have ~same y
# Hand up/down => volume up/down using pyautogui

import time
import cv2
import mediapipe as mp
import pyautogui

# -----------------------
# Settings (tune these)
# -----------------------
CAM_INDEX = 0
W, H = 640, 480

# How often to apply volume change when moving (seconds)
TICK_DT = 0.12          # ~8 updates/sec

# Ignore tiny up/down motion (normalized units)
Y_DEADBAND = 0.015      # try 0.01–0.03

# How strongly motion maps to repeated key presses
GAIN = 90.0             # higher = faster volume change
MAX_STEPS_PER_TICK = 3  # cap repeat rate

# Horizontal-hand detection (pinky points share ~same y)
USE_HORIZONTAL_GATE = True
PINKY_IDS = (17, 18, 19, 20)  # MCP, PIP, DIP, TIP
PINKY_Y_SPREAD_THRESH = 0.03  # lower=stricter, try 0.02–0.05

# Which landmarks to average for a stable palm point
PALM_IDS = (0, 5, 9, 13, 17)


def palm_center_norm(hand_landmarks, ids=PALM_IDS):
    lms = hand_landmarks.landmark
    x = sum(lms[i].x for i in ids) / len(ids)
    y = sum(lms[i].y for i in ids) / len(ids)
    return x, y


def pinky_horizontal(hand_landmarks, ids=PINKY_IDS, y_spread_thresh=PINKY_Y_SPREAD_THRESH):
    """
    Returns (is_horizontal, y_spread)
    y_spread = max_y - min_y for pinky landmarks.
    If spread is small, pinky is roughly level/horizontal.
    """
    lms = hand_landmarks.landmark
    ys = [lms[i].y for i in ids]
    spread = max(ys) - min(ys)
    return spread < y_spread_thresh, spread


def press_volume(direction: str, steps: int):
    key = "volumeup" if direction == "up" else "volumedown"
    for _ in range(steps):
        pyautogui.press(key)


def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    volume_mode = False
    baseline_y = None
    last_tick = 0.0

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as hands:

        while True:
            ok, frame = cap.read()
            if not ok:
                print("Failed to read camera frame.")
                break

            # Mirror preview for natural movement
            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            status_lines = []
            status_lines.append(f"Volume mode: {'ON' if volume_mode else 'OFF'}  (press 'v' to toggle)")

            if results.multi_hand_landmarks:
                hand_lms = results.multi_hand_landmarks[0]

                # Draw landmarks for debugging
                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

                # Palm COM point
                x, y = palm_center_norm(hand_lms)
                h, w = frame.shape[:2]
                cx, cy = int(x * w), int(y * h)
                cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                # Horizontal gate using pinky y-spread
                if USE_HORIZONTAL_GATE:
                    horiz_ok, spread = pinky_horizontal(hand_lms)
                    status_lines.append(
                        f"pinky_horizontal={horiz_ok} y_spread={spread:.3f} (thresh {PINKY_Y_SPREAD_THRESH})"
                    )
                else:
                    horiz_ok, spread = True, 0.0
                    status_lines.append("horizontal gate: OFF")

                # Volume control when in mode and horizontal
                if volume_mode and horiz_ok:
                    if baseline_y is None:
                        baseline_y = y
                        last_tick = time.time()
                        status_lines.append(f"baseline set: {baseline_y:.3f}")
                    else:
                        # y increases downward on image; moving hand UP makes y smaller
                        dy = baseline_y - y  # positive => up
                        status_lines.append(f"y={y:.3f} baseline={baseline_y:.3f} dy={dy:+.3f}")

                        now = time.time()
                        if now - last_tick >= TICK_DT:
                            last_tick = now

                            if abs(dy) >= Y_DEADBAND:
                                steps = int(min(MAX_STEPS_PER_TICK, max(1, abs(dy) * GAIN)))
                                direction = "up" if dy > 0 else "down"
                                status_lines.append(f"VOL: {direction} steps={steps}")
                                press_volume(direction, steps)
                            else:
                                status_lines.append("VOL: (deadband)")
                elif volume_mode and not horiz_ok:
                    status_lines.append("Volume mode ON but pinky not horizontal -> no volume change")

            else:
                status_lines.append("No hand detected.")
                if volume_mode:
                    status_lines.append("Tip: keep hand in view; press 'v' to re-baseline anytime.")

            # HUD
            y0 = 25
            for i, line in enumerate(status_lines[:12]):
                cv2.putText(
                    frame,
                    line,
                    (15, y0 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow("Volume Gesture Test (v toggle, q quit)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("v"):
                volume_mode = not volume_mode
                baseline_y = None  # re-baseline on toggle
                print(f"[DEBUG] Volume mode -> {'ON' if volume_mode else 'OFF'} (baseline reset)")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()