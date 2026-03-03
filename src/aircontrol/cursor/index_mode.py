# src/aircontrol/cursor/index_mode.py

class IndexCursorMode:

    INDEX_TIP_ID = 8

    def __init__(self):
        pass

    def get_point(self, hand_landmarks):
        if hand_landmarks is None:
            return None
        
        try:
            lms = hand_landmarks.landmark
            x = lms[self.INDEX_TIP_ID].x
            y = lms[self.INDEX_TIP_ID].y

            # safety clamp (protect against negative and infinite values)
            x_pt = min(max(x, 0.0), 1.0)
            y_pt = min(max(y, 0.0), 1.0)
        
            return (x_pt, y_pt)
        except (AttributeError, IndexError):
            return None