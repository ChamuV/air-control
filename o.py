import time
import cv2
import mediapipe as mp
import subprocess
from collections import deque

# -----------------------
# Camera
# -----------------------
CAM_INDEX = 0
W, H = 640, 480

# -----------------------
# Horizontal hand rule (your rule)
# -----------------------
PINKY_IDS = (17, 18, 19, 20)
PINKY_Y_SPREAD_THRESH = 0.03

# -----------------------
# Motion detection
# -----------------------
# landmarks to track for motion (palm + mcp joints is stable)
TRACK_IDS = (0, 5, 9, 13, 17)

# how many recent frames to keep for velocity estimate
HISTORY = 6  # 4–10

# minimum speed (normalized y per second) to consider movement real
# (remember: up is negative speed)
SPEED_THRESH = 0.15  # try 0.10–0.25

# require this fraction of tracked points to agree on direction
CONSENSUS_FRAC = 0.8

# apply volume change at most once per interval
TICK_DT = 0.15  # 0.10–0.25

# map speed magnitude -> volume step count
GAIN = 8.0             # higher = more aggressive
MAX_STEPS_PER_TICK = 3
DELTA_PER_STEP = 4      # volume points per step (0..100)

# -----------------------
# Volume control (macOS)
# -----------------------
def osascript(script: str) -> str:
    p = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return (p.stdout or "").strip()

def get_volume() -> int:
    return int(osascript("output volume of (get volume settings)"))

def set_volume(v: int) -> None:
    v = max(0, min(100, int(v)))
    osascript(f"set volume output volume {v}")

def change_volume_cached(current: int, direction: str, steps: int) -> int:
    steps = max(1, int(steps))
    delta = DELTA_PER_STEP * steps
    if direction == "down":
        delta = -delta
    new_v = max(0, min(100, current + delta))
    set_volume(new_v)
    return new_v

# -----------------------
# Helpers
# -----------------------
def pinky_horizontal(hand_landmarks):
    lms = hand_landmarks.landmark
    ys = [lms[i].y for i in PINKY_IDS]
    spread = max(ys) - min(ys)
    return spread < PINKY_Y_SPREAD_THRESH, spread

def tracked_y_values(hand_landmarks):
    lms = hand_landmarks.landmark
    return [lms[i].y for i in TRACK_IDS]

def overlay_lines(frame, lines, x=15, y0=25):
    for i, line in enumerate(lines[:14]):
        cv2.putText(
            frame,
            line,
            (x, y0 + i * 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

# -----------------------
# Main
# -----------------------
def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    volume_mode = False
    last_tick = 0.0

    # store history of (time, y_values list)
    hist = deque(maxlen=HISTORY)

    current_volume = get_volume()
    print("[INFO] Initial volume:", current_volume)
    print("[INFO] Controls: v toggle volume mode, q quit")

    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[ERROR] Camera read failed.")
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            now = time.time()
            status = [f"Volume mode: {'ON' if volume_mode else 'OFF'} (press v)", f"Volume: {current_volume}"]

            if results.multi_hand_landmarks:
                hand_lms = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

                horiz_ok, spread = pinky_horizontal(hand_lms)
                status.append(f"pinky_horizontal={horiz_ok} spread={spread:.3f} (th {PINKY_Y_SPREAD_THRESH})")

                if volume_mode and horiz_ok:
                    ys = tracked_y_values(hand_lms)
                    hist.append((now, ys))

                    if len(hist) >= 2:
                        t0, y0 = hist[0]
                        t1, y1 = hist[-1]
                        dt = max(1e-3, t1 - t0)

                        # compute per-point velocities
                        v = [(y1[i] - y0[i]) / dt for i in range(len(TRACK_IDS))]  # + means moving DOWN
                        v_avg = sum(v) / len(v)

                        # consensus direction count
                        up_votes = sum(1 for vi in v if vi < -SPEED_THRESH)
                        down_votes = sum(1 for vi in v if vi > SPEED_THRESH)
                        frac_up = up_votes / len(v)
                        frac_down = down_votes / len(v)

                        status.append(f"v_avg={v_avg:+.3f}  up_frac={frac_up:.2f} down_frac={frac_down:.2f} (thr {SPEED_THRESH})")

                        direction = None
                        if frac_up >= CONSENSUS_FRAC:
                            direction = "up"
                        elif frac_down >= CONSENSUS_FRAC:
                            direction = "down"

                        if direction is None:
                            status.append("motion: none/unstable")
                        else:
                            # apply at tick rate
                            if now - last_tick >= TICK_DT:
                                last_tick = now

                                # speed magnitude -> steps
                                speed_mag = abs(v_avg)
                                steps = int(min(MAX_STEPS_PER_TICK, max(1, speed_mag * GAIN)))
                                status.append(f"APPLY: {direction} steps={steps}")

                                try:
                                    current_volume = change_volume_cached(current_volume, direction, steps)
                                    print(f"[APPLY] {direction} steps={steps} -> {current_volume}")
                                except Exception as e:
                                    status.append("APPLY FAILED (see terminal)")
                                    print("[ERROR] set_volume failed:", e)

                else:
                    # reset history if you leave volume pose/mode (prevents stale velocity)
                    hist.clear()

            else:
                status.append("No hand detected.")
                hist.clear()

            overlay_lines(frame, status)
            cv2.imshow("Volume Gesture Velocity Test (macOS) - v toggle, q quit", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("v"):
                volume_mode = not volume_mode
                hist.clear()
                last_tick = 0.0
                print(f"[DEBUG] Volume mode -> {'ON' if volume_mode else 'OFF'} (history reset)")

    cap.release()
    cv2.destroyAllWindows()



main()