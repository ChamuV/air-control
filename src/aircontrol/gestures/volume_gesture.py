# src/aircontrol/gestures/volume_gesture.py

import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Tuple


@dataclass(frozen=True)
class VolumeSignal:
    direction: str   # "up" | "down"
    steps: int


class VolumeMotionGesture:
    """
    Horizontal-hand gated volume gesture using velocity + multi-point consensus.

    Horizontal condition: pinky joints (17,18,19,20) have nearly same y (your definition).
    Motion: track multiple landmarks; compute per-point y-velocity.
    Consensus: most points move in same direction with enough speed.
    Tick: emits at most once every tick_dt seconds.
    """

    PINKY_IDS = (17, 18, 19, 20)
    TRACK_IDS = (0, 5, 9, 13, 17)

    def __init__(
        self,
        pinky_y_spread_thresh: float = 0.03,
        history: int = 6,
        speed_thresh: float = 0.15,
        consensus_frac: float = 0.8,
        tick_dt: float = 0.15,
        gain: float = 8.0,
        max_steps_per_tick: int = 3,
    ):
        self.pinky_y_spread_thresh = float(pinky_y_spread_thresh)
        self.speed_thresh = float(speed_thresh)
        self.consensus_frac = float(consensus_frac)
        self.tick_dt = float(tick_dt)
        self.gain = float(gain)
        self.max_steps_per_tick = int(max_steps_per_tick)

        self._hist: Deque[Tuple[float, List[float]]] = deque(maxlen=int(history))
        self._last_tick = 0.0

    def reset(self):
        self._hist.clear()
        self._last_tick = 0.0

    def _pinky_horizontal(self, hand_landmarks) -> Tuple[bool, float]:
        lms = hand_landmarks.landmark
        ys = [lms[i].y for i in self.PINKY_IDS]
        spread = max(ys) - min(ys)
        return (spread < self.pinky_y_spread_thresh), spread

    def _tracked_ys(self, hand_landmarks) -> List[float]:
        lms = hand_landmarks.landmark
        return [lms[i].y for i in self.TRACK_IDS]

    def update(self, hand_landmarks) -> Tuple[Optional[VolumeSignal], dict]:
        now = time.time()

        horizontal_ok, spread = self._pinky_horizontal(hand_landmarks)
        debug = {
            "horizontal_ok": horizontal_ok,
            "pinky_spread": spread,
            "v_avg": None,
            "frac_up": None,
            "frac_down": None,
        }

        if not horizontal_ok:
            self.reset()
            return None, debug

        ys = self._tracked_ys(hand_landmarks)
        self._hist.append((now, ys))

        if len(self._hist) < 2:
            return None, debug

        t0, y0 = self._hist[0]
        t1, y1 = self._hist[-1]
        dt = max(1e-3, t1 - t0)

        v = [(y1[i] - y0[i]) / dt for i in range(len(self.TRACK_IDS))]
        v_avg = sum(v) / len(v)

        up_votes = sum(1 for vi in v if vi < -self.speed_thresh)
        down_votes = sum(1 for vi in v if vi > self.speed_thresh)
        frac_up = up_votes / len(v)
        frac_down = down_votes / len(v)

        debug["v_avg"] = v_avg
        debug["frac_up"] = frac_up
        debug["frac_down"] = frac_down

        direction = None
        if frac_up >= self.consensus_frac:
            direction = "up"
        elif frac_down >= self.consensus_frac:
            direction = "down"

        if direction is None:
            return None, debug

        if now - self._last_tick < self.tick_dt:
            return None, debug
        self._last_tick = now

        steps = int(min(self.max_steps_per_tick, max(1, abs(v_avg) * self.gain)))
        return VolumeSignal(direction=direction, steps=steps), debug