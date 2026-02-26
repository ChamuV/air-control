# src/aircontrol/gestures/features/center_of_mass.py

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

# Palm anchors
PALM_IDS = (0, 5, 9, 13, 17)


@dataclass(frozen=True)
class Point2D:
    x: float  # normalized [0,1]
    y: float  # normalized [0,1]


def center_of_mass(
    hand_landmarks,
    ids: Sequence[int] = PALM_IDS,
    image_size: Optional[Tuple[int, int]] = None,
):
    """
    Compute the center-of-mass (mean) of selected landmarks.

    Args:
        hand_landmarks: MediaPipe hand landmarks object (has .landmark list)
        ids: landmark indices to average (default = palm anchors)
        image_size: optional (width, height). If provided, returns pixel coords too.

    Returns:
        (norm_point, pixel_point_or_None)
        - norm_point: Point2D in normalized coords [0,1]
        - pixel_point_or_None: (x_px, y_px) if image_size given, else None
    """
    lms = hand_landmarks.landmark

    xs = [lms[i].x for i in ids]
    ys = [lms[i].y for i in ids]

    avg_x = sum(xs) / len(ids)
    avg_y = sum(ys) / len(ids)

    norm_point = Point2D(avg_x, avg_y)

    if image_size is None:
        return norm_point, None

    w, h = image_size
    px = int(avg_x * w)
    py = int(avg_y * h)

    return norm_point, (px, py)