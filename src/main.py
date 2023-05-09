from typing import List
import uvicorn
from fastapi  import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.requests import Request
from camera import Camera

allowed_hosts: List[str] = ["192.168.0.132"]

app = FastAPI()

def get_httpContent_generator(camera: Camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.get("/", response_class=PlainTextResponse)
async def index(request: Request):
    if request.client.host in allowed_hosts:
        return StreamingResponse(get_httpContent_generator(Camera()), media_type='multipart/x-mixed-replace; boundary=frame')

    return PlainTextResponse(status_code=400, content="Access Dinied.")

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.2", port=80)