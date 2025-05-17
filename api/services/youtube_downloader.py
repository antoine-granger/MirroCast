# api/services/youtube_downloader.py

import os
import subprocess

from .generate_thumbnail import generate_thumbnail

def download_video(url: str):
    MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "media"))
    os.makedirs(MEDIA_DIR, exist_ok=True)

    cmd = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "-o", os.path.join(MEDIA_DIR, "%(title)s.%(ext)s"),
        url
    ]
    subprocess.run(cmd)
    video_files = [f for f in os.listdir(MEDIA_DIR) if f.endswith(".mp4")]
    latest_video = max(
        video_files,
        key=lambda f: os.path.getctime(os.path.join(MEDIA_DIR, f))
    )
    video_path = os.path.join(MEDIA_DIR, latest_video)
    thumbnail_path = os.path.splitext(video_path)[0] + ".jpg"

    generate_thumbnail(video_path, thumbnail_path)
