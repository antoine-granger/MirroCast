import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.routers import download, stream, webrtc

app = FastAPI()
app.include_router(download.router)
app.include_router(stream.router)
app.include_router(webrtc.router)

app.mount("/media", StaticFiles(directory="media"), name="media")

# Autoriser le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://192.168.1.128:5173",
        "http://localhost:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello from MirroCast!"}

@app.get("/videos")
def get_videos():
    files = os.listdir("media/")
    return {"videos": [f for f in files if f.endswith(('.mp4', '.mkv'))]}
