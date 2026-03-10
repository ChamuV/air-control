# src/aircontrol/ui/gesture_hud.py

from __future__ import annotations

from pathlib import Path

import cv2
import yaml


_MAPPING_CACHE: dict[str, str] | None = None


def load_gesture_mapping(path: str = "config/gesture_action_map.yaml") -> dict:
    global _MAPPING_CACHE

    if _MAPPING_CACHE is None:
        p = Path(path)
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                _MAPPING_CACHE = yaml.safe_load(f) or {}
        else:
            _MAPPING_CACHE = {}

    return _MAPPING_CACHE


def draw_gesture_hud(
    frame,
    gesture_name: str | None = None,
    progress: float = 0.0,
    mapping_path: str = "config/gesture_action_map.yaml",
) -> None:
    h, w = frame.shape[:2]

    mapping = load_gesture_mapping(mapping_path)

    if gesture_name:
        mapped_action = mapping.get(gesture_name, "unmapped")
        label = gesture_name
        action_text = str(mapped_action)
    else:
        label = "None"
        action_text = "-"

    panel_w = 260
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
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        action_text,
        (x0 + 20, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )

    cx = x0 + 70
    cy = 185
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
        (x0 + 120, 193),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (220, 220, 220),
        2,
        cv2.LINE_AA,
    )