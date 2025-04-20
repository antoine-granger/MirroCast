import subprocess

def start_nvenc_stream():
    cmd = [
        'ffmpeg',
        '-f', 'gdigrab',
        '-framerate', '60',
        '-i', 'desktop',
        '-c:v', 'h264_nvenc',
        '-preset', 'p1',           # rapide
        '-b:v', '6000k',           # bitrate cible
        '-f', 'mjpeg',             # MJPEG pour test simple dans navigateur
        'http://0.0.0.0:8090'
    ]

    print("🚀 Lancement de NVENC Streamer avec RTX 3060 Ti...")
    subprocess.run(cmd)

if __name__ == "__main__":
    start_nvenc_stream()
