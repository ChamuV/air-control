# src/aircontrol/gestures/pinch.py

import pyautogui
import math

class PinchDetector:
    """
    Detects pinch between thumb tip and index.
    """

    THUMB_TIP = 4
    INDEX_TIP = 8

    def __init__(self, threshold: float = 0.04):
        """
        threshold: distance in normalized coords (0–1)
        Smaller = stricter pinch
        """
        self.threshold = threshold
        self.prev_state = False  # for edge detection

    def detect(self, hand_landmarks):
        lms = hand_landmarks.landmark

        dx = lms[self.THUMB_TIP].x - lms[self.INDEX_TIP].x
        dy = lms[self.THUMB_TIP].y - lms[self.INDEX_TIP].y

        distance = math.hypot(dx, dy)

        is_pinched = distance < self.threshold

        # Detect rising edge
        just_pinched = is_pinched and not self.prev_state

        self.prev_state = is_pinched

        return just_pinched