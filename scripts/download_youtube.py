import os
import subprocess
import sys

MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "media"))

def download_youtube(url: str):
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)

    print(f"Téléchargement de la vidéo depuis : {url}")
    cmd = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mkv",
        "-o", os.path.join(MEDIA_DIR, "%(title)s.%(ext)s"),
        url
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_youtube.py <url_youtube>")
    else:
        download_youtube(sys.argv[1])