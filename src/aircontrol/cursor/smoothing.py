# src/aircontrol/cursor/smoothing.py

class EMAFilter2D:
    def __init__(self, alpha=0.15):
        self.alpha = float(alpha)
        self.prev_x = None
        self.prev_y = None
        self.initialized = False

    def update(self, x, y):
        x = float(x)
        y = float(y)

        if not self.initialized:
            self.initialized = True
            self.prev_x = x
            self.prev_y = y
            return (x, y)

        a = self.alpha
        xs = a * x + (1.0 - a) * self.prev_x
        ys = a * y + (1.0 - a) * self.prev_y

        self.prev_x = xs
        self.prev_y = ys

        return (xs, ys)

    def reset(self):
        self.initialized = False
        self.prev_x = None
        self.prev_y = None