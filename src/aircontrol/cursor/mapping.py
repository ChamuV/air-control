# src/aircontrol/cursor/mapping.py

from __future__ import annotations


def map_norm_to_screen(
    x_norm: float,
    y_norm: float,
    screen_w: int,
    screen_h: int,
) -> tuple[float, float]:
    """
    Map normalized hand coordinates (0..1) from camera space
    into screen pixel coordinates.

    The camera workspace is cropped to a comfortable hand-movement box,
    then stretched to fill the full screen.

    This helps:
    - reach the bottom of the screen more easily
    - avoid needing to move your hand to the extreme edges of the webcam frame
    """

    # Comfortable usable workspace inside camera frame
    x_min, x_max = 0.08, 0.92
    y_min, y_max = 0.05, 0.78

    # Re-normalize from cropped workspace -> [0, 1]
    x = (x_norm - x_min) / (x_max - x_min)
    y = (y_norm - y_min) / (y_max - y_min)

    # Clamp to valid range
    x = max(0.0, min(1.0, x))
    y = max(0.0, min(1.0, y))

    # Map to screen space.
    # Leave a 1px margin so PyAutoGUI failsafe corners are avoided.
    px = x * (screen_w - 2) + 1
    py = y * (screen_h - 2) + 1

    return px, py