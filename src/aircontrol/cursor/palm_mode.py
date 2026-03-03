# src/aircontrol/cursor/palm_mode.py


class PalmCursorMode:

    PALM_IDS = (0, 5, 9, 13, 17)

    def __init__(self):
        pass
        
    def get_point(self, hand_landmarks):
        """
        Return (x_norm, y_norm) in range [0,1] or None.
        """
        if hand_landmarks is None:
            return None
        
        try:
            lms = hand_landmarks.landmark
            xs = [lms[i].x for i in self.PALM_IDS]
            ys = [lms[i].y for i in self.PALM_IDS]
            
            x_norm = sum(xs) / len(xs)
            y_norm = sum(ys) / len(ys)

            # safety clamp (protect against negative and infinite values)
            x_norm = min(max(x_norm, 0.0), 1.0)
            y_norm = min(max(y_norm, 0.0), 1.0)

            return (x_norm, y_norm)
        except (AttributeError, IndexError):
            return None
