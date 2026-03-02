# src/aircontrol/gestures/window_gesture.py

import time
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class WindowSignal:
    direction: str  # "right" | "left"


class WindowMotionGesture:
    """
    Fingertip-based window swipe gesture.

    Pose gate:
      1) Fingertips (index/middle/ring/pinky tips: 8,12,16,20) have ~same x (small x-spread)
      2) "Other points behind it": for each finger, tip is ahead of MCP along x by min_extension_x
         and most fingers agree on direction (to make the pose intentional).

    Swipe trigger:
      - Track mean x of the fingertip cluster
      - If moved by >= swipe_dist_thresh, emit exactly one signal and reset baseline
      - Cooldown tick_dt prevents rapid repeats

    Mapping:
      - hand moves RIGHT -> LEFT  => dx negative => next window on RIGHT  => direction="right"
      - hand moves LEFT -> RIGHT  => dx positive => next window on LEFT   => direction="left"
    """

    TIP_IDS = (8, 12, 16, 20)     # fingertips
    MCP_IDS = (5, 9, 13, 17)      # corresponding MCP joints

    def __init__(
        self,
        tip_x_spread_thresh: float = 0.05,
        min_extension_x: float = 0.03,
        swipe_dist_thresh: float = 0.10,
        tick_dt: float = 0.40,
    ):
        self.tip_x_spread_thresh = float(tip_x_spread_thresh)
        self.min_extension_x = float(min_extension_x)
        self.swipe_dist_thresh = float(swipe_dist_thresh)
        self.tick_dt = float(tick_dt)

        self._baseline_x: Optional[float] = None
        self._last_tick: float = 0.0

    def reset(self) -> None:
        self._baseline_x = None

    def _tips_mean_x_and_spread(self, hand_landmarks) -> Tuple[float, float]:
        lms = hand_landmarks.landmark
        xs = [lms[i].x for i in self.TIP_IDS]
        mean_x = sum(xs) / len(xs)
        spread = max(xs) - min(xs)
        return mean_x, spread

    def _tips_are_stacked(self, hand_landmarks) -> Tuple[bool, float, float]:
        mean_x, spread = self._tips_mean_x_and_spread(hand_landmarks)
        return (spread < self.tip_x_spread_thresh), mean_x, spread

    def _fingers_behind_tips(self, hand_landmarks) -> bool:
        """
        Require that at least 3/4 fingers have |tip_x - mcp_x| >= min_extension_x
        AND that those strong fingers mostly agree on sign (all pointing same way in x).
        """
        lms = hand_landmarks.landmark

        deltas = []
        for tip_id, mcp_id in zip(self.TIP_IDS, self.MCP_IDS):
            deltas.append(lms[tip_id].x - lms[mcp_id].x)

        strong = [d for d in deltas if abs(d) >= self.min_extension_x]
        if len(strong) < 3:
            return False

        pos = sum(1 for d in strong if d > 0)
        neg = sum(1 for d in strong if d < 0)
        return (pos >= 3) or (neg >= 3)

    def update(self, hand_landmarks):
        """
        Returns: (WindowSignal | None, debug_dict)

        debug_dict keys:
          pose_ok: bool
          tips_spread: float
          dx: float | None
        """
        now = time.time()

        tips_stacked, mean_x, spread = self._tips_are_stacked(hand_landmarks)
        behind_ok = self._fingers_behind_tips(hand_landmarks)
        pose_ok = tips_stacked and behind_ok

        debug = {"pose_ok": pose_ok, "tips_spread": spread, "dx": None}

        if not pose_ok:
            self.reset()
            return None, debug

        if self._baseline_x is None:
            self._baseline_x = mean_x
            self._last_tick = now
            return None, debug

        dx = mean_x - self._baseline_x
        debug["dx"] = dx

        if now - self._last_tick < self.tick_dt:
            return None, debug

        if abs(dx) < self.swipe_dist_thresh:
            return None, debug

        self._last_tick = now
        self._baseline_x = mean_x

        # mapping
        if dx < 0:
            return WindowSignal(direction="right"), debug
        else:
            return WindowSignal(direction="left"), debug