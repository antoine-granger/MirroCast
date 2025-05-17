import subprocess
import os
from pathlib import Path
import socket
import time

ffmpeg_process = None

def get_free_udp_port():
    """Trouver un port UDP libre sans le bloquer"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def wait_for_rtp_packets(port, timeout=3.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", port))
    sock.settimeout(timeout)
    try:
        print(f"⏳ En attente de premier paquet RTP sur {port}...")
        data, addr = sock.recvfrom(2048)
        print(f"✅ Premier paquet RTP reçu de {addr} ({len(data)} octets)")
    except socket.timeout:
        raise TimeoutError(f"❌ Aucun paquet RTP reçu sur le port {port} après {timeout} secondes.")
    finally:
        sock.close()


def start_ffmpeg():
    global ffmpeg_process

    port = get_free_udp_port()
    print(f"🚀 Port UDP sélectionné : {port}")

    ffmpeg_command = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "testsrc=size=1280x720:rate=30",

        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-profile:v", "baseline",
        "-level", "3.1",
        "-g", "15",
        "-keyint_min", "15",
        "-x264-params", "repeat-headers=1:annexb=1",
        "-pix_fmt", "yuv420p",
        "-f", "rtp",
        f"rtp://127.0.0.1:{port}",
        "-loglevel", "debug"
    ]

    print("🖥️ Démarrage de FFmpeg pour émission RTP...")

    ffmpeg_process = subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )

    # Petite attente pour s'assurer que ffmpeg commence
    time.sleep(1)

    return port
