from fastapi import APIRouter
from threading import Thread
from api.services.screen_capture import capture_frame
from fastapi.responses import StreamingResponse
import time

router = APIRouter()

mirroring_enabled = False

def mjpeg_stream():
    while mirroring_enabled:
        frame = capture_frame()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               frame +
               b"\r\n")
        time.sleep(1 / 30)

@router.get("/mirror/mjpeg")
async def mirror_mjpeg():
    if not mirroring_enabled:
        return {"error": "Mirroring is disabled."}
    return StreamingResponse(mjpeg_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/mirror/start")
async def start_mirroring():
    global mirroring_enabled
    mirroring_enabled = True
    return {"status": "mirroring started"}

@router.post("/mirror/stop")
async def stop_mirroring():
    global mirroring_enabled
    mirroring_enabled = False
    return {"status": "mirroring stopped"}
