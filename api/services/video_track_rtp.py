import av
import asyncio
import socket
import time
from pathlib import Path
from aiortc import VideoStreamTrack
from av.video.frame import VideoFrame
from av.error import InvalidDataError

SDP_ORIGINAL = Path(__file__).resolve().parent.parent / "static" / "stream.sdp"
SDP_PATCHED = Path(__file__).resolve().parent.parent / "static" / "patched_stream.sdp"

class RtpVideoStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()

        # Démarrage FFmpeg
        from api.services.ffmpeg_launcher import start_ffmpeg
        start_ffmpeg()

        # Attente fichier SDP généré
        timeout = 5
        t0 = time.time()
        while not SDP_ORIGINAL.exists() or SDP_ORIGINAL.stat().st_size < 50:
            if time.time() - t0 > timeout:
                raise RuntimeError("Timeout : stream.sdp non disponible.")
            time.sleep(0.1)

        # Patch SDP pour PyAV
        sdp_text = SDP_ORIGINAL.read_text()
        if "a=control:streamid=0" not in sdp_text:
            sdp_text += "\na=control:streamid=0\n"
        SDP_PATCHED.write_text(sdp_text)
        print("🩹 SDP copié + patché dans", SDP_PATCHED)

        # 🔍 Attente active de réception d’un paquet RTP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10.0)
        sock.bind(("127.0.0.1", 5006))
        try:
            data, addr = sock.recvfrom(2048)
            print(f"📦 Paquet RTP reçu de {addr} ({len(data)} octets)")
        except socket.timeout:
            raise RuntimeError("❌ Aucun paquet RTP reçu dans le délai imparti (10s)")
        finally:
            sock.close()

        # ✅ Ouverture PyAV avec options anti-buffering
        try:
            self.container = av.open(
                str(SDP_PATCHED),
                options={
                    "protocol_whitelist": "file,udp,rtp",
                    "fifo_size": "0",
                    "overrun_nonfatal": "1"
                }
            )
        except InvalidDataError as e:
            raise RuntimeError("Erreur lors de l'ouverture du SDP : " + str(e)) from e

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        for packet in self.container.demux(video=0):  # 👈 plus rapide
            for frame in packet.decode():
                if isinstance(frame, VideoFrame):
                    frame.pts = pts
                    frame.time_base = time_base
                    return frame
        await asyncio.sleep(0.005)
        return await self.recv()
