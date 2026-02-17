import time
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_PATH = "models/hand_landmarker.task"  # <-- adjust if needed


@dataclass
class LatestResult:
    result: Optional[vision.HandLandmarkerResult] = None
    timestamp_ms: int = 0


LATEST = LatestResult()


def _result_callback(result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    # Called asynchronously in LIVE_STREAM mode
    LATEST.result = result
    LATEST.timestamp_ms = timestamp_ms


def _is_thumb_extended(lms, handedness: str) -> bool:
    # Landmarks are normalized [0,1] in image coords.
    # This heuristic assumes palm facing camera reasonably.
    # Thumb extension: compare x of THUMB_TIP vs THUMB_IP based on handedness
    tip = lms[4]   # THUMB_TIP
    ip  = lms[3]   # THUMB_IP

    if handedness == "Right":
        return tip.x < ip.x
    else:
        return tip.x > ip.x


def _is_finger_extended(lms, tip_i: int, pip_i: int, mcp_i: int) -> bool:
    # For non-thumb fingers: extended if tip is above pip and pip above mcp (y smaller is "up")
    tip = lms[tip_i]
    pip = lms[pip_i]
    mcp = lms[mcp_i]
    return (tip.y < pip.y) and (pip.y < mcp.y)


def is_stop_open_palm(lms, handedness: str) -> Tuple[bool, int]:
    """
    STOP = open palm: thumb + 4 fingers extended (5 total).
    Returns (is_stop, extended_count).
    """
    extended = 0

    if _is_thumb_extended(lms, handedness):
        extended += 1

    # index, middle, ring, pinky
    finger_defs = [
        (8, 6, 5),    # INDEX_TIP, INDEX_PIP, INDEX_MCP
        (12, 10, 9),  # MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP
        (16, 14, 13), # RING_TIP, RING_PIP, RING_MCP
        (20, 18, 17), # PINKY_TIP, PINKY_PIP, PINKY_MCP
    ]

    for tip_i, pip_i, mcp_i in finger_defs:
        if _is_finger_extended(lms, tip_i, pip_i, mcp_i):
            extended += 1

    return (extended == 5), extended


def main():
    # Build the hand landmarker (Tasks API)
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
        result_callback=_result_callback,
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Try a different camera index (0, 1, ...).")

    # Optional: mirror view for user-friendly display
    MIRROR = True

    # Simple cooldown so "STOP" doesn’t spam
    last_stop_time = 0.0
    STOP_COOLDOWN_S = 0.75

    while True:
        ok, frame_bgr = cap.read()
        if not ok:
            break

        if MIRROR:
            frame_bgr = cv2.flip(frame_bgr, 1)

        # Convert to MediaPipe Image
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, timestamp_ms)

        # Read latest async result (may be None if callback hasn't fired yet)
        label_text = "No hand"
        r = LATEST.result

        if r and r.hand_landmarks and len(r.hand_landmarks) > 0:
            lms = r.hand_landmarks[0]

            handedness = "Unknown"
            if r.handedness and len(r.handedness) > 0 and len(r.handedness[0]) > 0:
                handedness = r.handedness[0][0].category_name  # "Left" or "Right"

            stop, count = is_stop_open_palm(lms, handedness)
            label_text = f"{handedness} | extended={count}"

            # Draw landmarks (basic)
            h, w = frame_bgr.shape[:2]
            for lm in lms:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame_bgr, (cx, cy), 4, (255, 255, 255), -1)

            if stop:
                label_text = "STOP ✋"
                now = time.time()
                if (now - last_stop_time) > STOP_COOLDOWN_S:
                    last_stop_time = now
                    print("STOP")  # <-- Replace with your action

        # HUD
        cv2.rectangle(frame_bgr, (10, 10), (260, 60), (0, 0, 0), -1)
        cv2.putText(frame_bgr, label_text, (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("STOP gesture (MediaPipe Tasks)", frame_bgr)
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord("q")):
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()