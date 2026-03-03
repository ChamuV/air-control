# src/aircontrol/actions/camera_control.py

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

import cv2


class CameraScreenshotController:
    """
    Saves the latest BGR camera frame to disk.
    """

    def __init__(self, out_dir: str = "captures"):
        self.out_dir = out_dir
        Path(self.out_dir).mkdir(parents=True, exist_ok=True)

    def save_frame(self, frame_bgr) -> Optional[str]:
        if frame_bgr is None:
            return None

        ts = time.strftime("%Y%m%d-%H%M%S")
        path = os.path.join(self.out_dir, f"camera_{ts}.png")
        ok = cv2.imwrite(path, frame_bgr)
        return path if ok else None