# src/aircontrol/tracking/hand_tracker.py

import cv2
import mediapipe as mp


class HandTracker:
    def __init__(
            self,
        static_image_mode: bool = False,
        max_num_hands: int = 1,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.6,
        draw_landmarks: bool = False,
    ):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self.draw_landmarks = draw_landmarks

    def process(self, frame_bgr):
        """
        Returns:
            hands_out: list[dict], each dict:
                {
                  "landmarks": hand_landmarks,   # mediapipe landmark object (21 pts)
                  "handedness": "Left"/"Right"/None
                }
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        hands_out = []
        if not results.multi_hand_landmarks:
            return hands_out

        for i, hand_lms in enumerate(results.multi_hand_landmarks):
            if self.draw_landmarks:
                self.mp_draw.draw_landmarks(
                    frame_bgr,
                    hand_lms,
                    self.mp_hands.HAND_CONNECTIONS,
                )

            handed = None
            if results.multi_handedness and i < len(results.multi_handedness):
                handed = results.multi_handedness[i].classification[0].label  # "Left"/"Right"

            hands_out.append({"landmarks": hand_lms, "handedness": handed})

        return hands_out

    def close(self):
        self.hands.close()