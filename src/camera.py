import numpy as np
import numpy.typing as npt
import threading
import cv2

class Camera:
    video = None
    thread: threading.Thread = None
    image: npt.NDArray[np.uint8] = None
    event: threading.Event = None
    last_index: int = None
    
    def __init__(self, index = 0) -> None:
        if Camera.video is None:
            Camera.thread = threading.Thread(target=Camera.frames, kwargs={"index": index})
            Camera.thread.start()
            Camera.event = threading.Event()
    
    def __del__(self) -> None:
        Camera.video.release()
    
    def get_frame(self):
        Camera.event.wait()
        Camera.event.clear()
        if Camera.image is None:
            return None
        _, encoded = cv2.imencode('.jpg', Camera.image)
        frame: bytes = encoded.tobytes()
        return frame
    
    @staticmethod
    def frames(index: int):
        Camera.video = cv2.VideoCapture(index)
        while True:
            _, image = Camera.video.read()
            Camera.image = image
            Camera.event.set()