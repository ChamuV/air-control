# src/aircontrol/tracking/hand_landmarks.py

import math

"""
MediaPipe Hand Landmark indices.

These constants correspond to the 21 landmarks returned by MediaPipe Hands.
Keeping them centralized avoids duplication across gesture detectors.
"""

# Wrist
WRIST = 0

# Thumb
THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4

# Index finger
INDEX_MCP = 5
INDEX_PIP = 6
INDEX_DIP = 7
INDEX_TIP = 8

# Middle finger
MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_DIP = 11
MIDDLE_TIP = 12

# Ring finger
RING_MCP = 13
RING_PIP = 14
RING_DIP = 15
RING_TIP = 16

# Pinky
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20


# Useful groups
FINGER_TIPS = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]

FINGER_MCPS = [INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP]

PALM_POINTS = [WRIST, INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP]


# Helper function
def dist(*args) -> float:
    """
    Distance between two landmarks.

    Supported forms:
        dist(lms, i, j)
        dist(p, q)
    """
    if len(args) == 3:
        lms, i, j = args
        p = lms[i]
        q = lms[j]

    elif len(args) == 2:
        p, q = args

    else:
        raise TypeError(
            "dist() expects either (lms, i, j) or (p, q)"
        )

    dx = p.x - q.x
    dy = p.y - q.y
    return math.hypot(dx, dy)