from fastapi import APIRouter, Request
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.rtcrtpsender import RTCRtpSender

from api.services.screen_capture import ScreenVideoTrack

router = APIRouter()

# 🌐 ICE Servers (STUN + TURN)
ICE_SERVERS = [
    RTCIceServer(
        urls="stun:stun.l.google.com:19302"
    ),
    RTCIceServer(
        urls="turn:192.168.1.128:3478",
        username="user",
        credential="pass"
    )
]


@router.post("/webrtc/offer")
async def webrtc_offer(request: Request):
    body = await request.json()
    offer = RTCSessionDescription(sdp=body["sdp"], type=body["type"])

    config = RTCConfiguration(iceServers=ICE_SERVERS)
    pc = RTCPeerConnection(configuration=config)

    user_agent = request.headers.get("user-agent", "").lower()
    if "android" in user_agent:
        print("📱 Android détecté : testsrc utilisé")
        from aiortc.contrib.media import MediaPlayer
        player = MediaPlayer("testsrc=size=640x480:rate=30", format="lavfi")
        pc.addTrack(player.video)
    else:
        track = ScreenVideoTrack(fps=60)
        pc.addTrack(track)

    # 🎯 Forcer l'utilisation du codec H264 (nécessaire pour iOS / WebOS)
    capabilities = RTCRtpSender.getCapabilities("video")
    h264_codecs = [c for c in capabilities.codecs if "H264" in c.mimeType]

    for transceiver in pc.getTransceivers():
        if transceiver.kind == "video":
            transceiver.setCodecPreferences(h264_codecs)
            transceiver.direction = "sendonly"

    print("🎯 Codecs H264 disponibles :", h264_codecs)

    await pc.setRemoteDescription(offer)

    print("📡 Local candidates (avant setLocalDescription):")
    for transceiver in pc.getTransceivers():
        sender = transceiver.sender
        if sender and sender.track:
            print("  Track:", sender.track.kind)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }
