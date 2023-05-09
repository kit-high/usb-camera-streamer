import numpy as np
import numpy.typing as npt
import threading
import cv2

class Camera:
    video = None
    thread: threading.Thread = None
    image: npt.NDArray[np.uint8] = None
    event_get_frame: threading.Event = None
    event_stop_thread: threading.Event = None
    last_index: int = None
    
    def __init__(self, index = 0) -> None:
        if Camera.video is None:
            Camera.thread = threading.Thread(target=Camera.frames, kwargs={"index": index})
            Camera.thread.start()
            Camera.event_get_frame = threading.Event()
            Camera.event_stop_thread = threading.Event()
    
    def stop() -> None:
        Camera.event_stop_thread.set()
        Camera.video.release()
        Camera.video = None
    
    def get_frame(self):
        Camera.event_get_frame.wait()
        Camera.event_get_frame.clear()
        if Camera.image is None:
            return None
        _, encoded = cv2.imencode('.jpg', Camera.image)
        frame: bytes = encoded.tobytes()
        return frame
    
    @staticmethod
    def frames(index: int):
        Camera.video = cv2.VideoCapture(index)
        Camera.last_index = index
        while True:
            if Camera.event_stop_thread.is_set():
                break
            _, image = Camera.video.read()
            Camera.image = image
            Camera.event_get_frame.set()