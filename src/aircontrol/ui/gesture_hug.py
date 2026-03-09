# src/aircontrol/ui/gesture_hug.py

from __future__ import annotations

import cv2


def draw_gesture_hud(frame, label: str = "None", progress: float = 0.0) -> None:
    h, w = frame.shape[:2]

    panel_w = 220
    x0 = w - panel_w

    cv2.rectangle(frame, (x0, 0), (w, h), (25, 25, 25), -1)

    cv2.putText(
        frame,
        "GESTURE",
        (x0 + 20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        label,
        (x0 + 20, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cx = x0 + 70
    cy = 160
    r = 28

    cv2.circle(frame, (cx, cy), r, (90, 90, 90), 2)

    progress = max(0.0, min(1.0, progress))
    end_angle = int(360 * progress)

    if progress > 0:
        cv2.ellipse(
            frame,
            (cx, cy),
            (r, r),
            -90,
            0,
            end_angle,
            (0, 220, 255),
            4,
        )

    cv2.putText(
        frame,
        f"{int(progress * 100)}%",
        (x0 + 120, 168),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (220, 220, 220),
        2,
        cv2.LINE_AA,
    )