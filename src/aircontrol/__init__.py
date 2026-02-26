# src/aircontrol/__init__.py
__version__ = "0.1.0"

from .camera.camera import Camera
from .tracking.hand_tracker import HandTracker
#from .actions.mouse_control import MouseController

__all__ = [
    "Camera",
    "HandTracker",
    #"MouseController",
]