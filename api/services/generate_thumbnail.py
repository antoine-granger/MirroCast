import subprocess


def generate_thumbnail(video_path: str, output_path: str):
    cmd = [
        "ffmpeg",
        "-ss", "00:00:03",  # Position dans la vidéo
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
