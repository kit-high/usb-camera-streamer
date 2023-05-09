from typing import List
import uvicorn
from fastapi  import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.requests import Request
from camera import Camera

allowed_hosts: List[str] = ["192.168.0.2"]

app = FastAPI()

def get_httpContent_generator(camera: Camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def isCameraIdChanged(camera_id: int) -> bool:
    return Camera.last_index != camera_id and Camera.thread is not None

def get_camera_response(camera_id: int, client_host: str):
    if isCameraIdChanged(camera_id):
        Camera.stop()
    if client_host in allowed_hosts:
        return StreamingResponse(get_httpContent_generator(Camera(camera_id)), media_type='multipart/x-mixed-replace; boundary=frame')
    return PlainTextResponse(status_code=400, content="Access Dinied.")

@app.get("/", response_class=PlainTextResponse)
async def index(request: Request):
    return get_camera_response(camera_id=0, client_host=request.client.host)

@app.get("/{camera_id}", response_class=PlainTextResponse)
async def index_camera_id(camera_id: int, request: Request):
    return get_camera_response(camera_id, client_host=request.client.host)

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.2", port=80)