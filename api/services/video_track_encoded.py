import asyncio
import socket
import logging
from fractions import Fraction
from pathlib import Path
import re

from av.packet import Packet
from aiortc import MediaStreamTrack
from aiortc.rtcrtpparameters import RTCRtpCodecParameters

VIDEO_CLOCK_RATE = 90000

SDP_PATH = Path(__file__).resolve().parent.parent / "static" / "stream.sdp"

def parse_sdp_payload_info(sdp_path: Path) -> dict:
    with open(sdp_path, "r") as f:
        content = f.read()

    payload_type = int(re.search(r"m=video \d+ RTP/AVP (\d+)", content).group(1))
    clock_rate = int(re.search(r"rtpmap:\d+ H264/(\d+)", content).group(1))
    fmtp_line = re.search(r"fmtp:\d+ ([^\n]+)", content).group(1)

    parameters = dict(pair.split('=') for pair in fmtp_line.split(';') if '=' in pair)

    return {
        "payloadType": payload_type,
        "clockRate": clock_rate,
        "parameters": parameters
    }

class H264PassthroughTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, port: int = None):
        super().__init__()
        self.queue = asyncio.Queue()
        self.timestamp = 0
        self.port = port or self._get_port_from_sdp()
        self._wait_for_rtp_packet(timeout=3.0)
        self._start_receiver()

    def _start_receiver(self):
        import threading
        def recv():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("127.0.0.1", self.port))
            logging.info(f"🎧 Listening on UDP 127.0.0.1:{self.port}")
            while True:
                try:
                    data, addr = sock.recvfrom(2048)
                    self.queue.put_nowait(data)
                except Exception as e:
                    logging.error(f"❌ Error receiving RTP: {e}")
                    break
        threading.Thread(target=recv, daemon=True).start()

    def _get_port_from_sdp(self):
        with open(SDP_PATH, "r") as f:
            for line in f:
                if line.startswith("m=video"):
                    return int(line.split()[1])

    def _wait_for_rtp_packet(self, timeout=3.0):
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_sock.settimeout(timeout)
        temp_sock.bind(("127.0.0.1", self.port))
        try:
            print(f"🧪 Attente de RTP sur {self.port}...")
            data, addr = temp_sock.recvfrom(2048)
            print(f"✅ Premier paquet RTP reçu depuis {addr} ({len(data)} bytes)")
        except socket.timeout:
            print("❌ Timeout : Aucun paquet RTP reçu")
        finally:
            temp_sock.close()

    async def recv(self) -> Packet:
        payload = await self.queue.get()
        self.timestamp += 3000  # ~33ms à 90kHz (30fps)
        pkt = Packet(payload)
        pkt.pts = self.timestamp
        pkt.dts = self.timestamp
        pkt.time_base = Fraction(1, VIDEO_CLOCK_RATE)
        return pkt

    @property
    def codec(self):
        info = parse_sdp_payload_info(SDP_PATH)
        print("🎥 Codec .codec() appelé")
        print(f"📍 clockRate = {info['clockRate']}")
        print(f"📍 parameters = {info['parameters']}")

        from aiortc.rtcrtpsender import RTCRtpSender
        capabilities = RTCRtpSender.getCapabilities("video")
        h264_codecs = [c for c in capabilities.codecs if c.mimeType == "video/H264"]

        for codec in h264_codecs:
            # match on clockRate only (we can override parameters)
            if codec.clockRate == info["clockRate"]:
                codec.parameters.update(info["parameters"])
                return codec

        raise ValueError("❌ Aucun codec H264 compatible trouvé dans les capabilities")

