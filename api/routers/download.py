# api/routers/download.py

from fastapi import APIRouter, BackgroundTasks
from api.models.video import VideoRequest
from api.services.youtube_downloader import download_video

router = APIRouter()

@router.post("/download")
async def download(video: VideoRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(download_video, video.url)
    return {"message": "Téléchargement lancé."}