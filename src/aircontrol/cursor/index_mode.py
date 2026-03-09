# src/aircontrol/cursor/index_mode.py

class IndexCursorMode:
    INDEX_TIP_ID = 8
    INDEX_PIP_ID = 6

    def __init__(self, tip_weight: float = 0.7, pip_weight: float = 0.3):
        self.tip_weight = float(tip_weight)
        self.pip_weight = float(pip_weight)

    def get_point(self, hand_landmarks):
        if hand_landmarks is None:
            return None

        try:
            lms = hand_landmarks.landmark

            tip = lms[self.INDEX_TIP_ID]
            pip = lms[self.INDEX_PIP_ID]

            # Weighted point: steadier than fingertip alone
            x = self.tip_weight * tip.x + self.pip_weight * pip.x
            y = self.tip_weight * tip.y + self.pip_weight * pip.y

            x_pt = min(max(x, 0.0), 1.0)
            y_pt = min(max(y, 0.0), 1.0)

            return (x_pt, y_pt)

        except (AttributeError, IndexError):
            return None