# src/aircontrol/camera/camera.py

import cv2


class Camera:
    """
    Simple webcam wrapper.
    Handles frame capture and display.
    """

    def __init__(self, width: int = 640, height: int = 480, cam_index: int = 0):
        self.cap = cv2.VideoCapture(cam_index)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            raise RuntimeError("Failed to read frame from camera.")
        return frame

    def show(self, frame, window_name: str = "AirControl", flip: bool = True):
        if flip:
            frame = cv2.flip(frame, 1)
        cv2.imshow(window_name, frame)

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()