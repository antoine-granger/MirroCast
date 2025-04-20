#/api/services/screen_capture.py

import time
import fractions
import asyncio
import cv2
import mss
import numpy as np
from aiortc.mediastreams import MediaStreamTrack
from av import VideoFrame

class ScreenVideoTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, fps=30):
        super().__init__()
        self.fps = fps
        self.interval = 1 / fps
        self.last_frame_time = time.time()
        self.start_time = time.time()
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

    async def recv(self):
        # Attente pour respecter le framerate
        while True:
            now = time.time()
            if now - self.last_frame_time >= self.interval:
                self.last_frame_time = now
                break
            await asyncio.sleep(0.001)

        # Capture l’écran
        img = np.array(self.sct.grab(self.monitor))
        frame_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Création du frame WebRTC
        frame = VideoFrame.from_ndarray(frame_bgr, format="bgr24")
        frame.pts = int((time.time() - self.start_time) * 90000)  # 90kHz
        frame.time_base = fractions.Fraction(1, 90000)

        return frame
