from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer, RTCRtpSender
from aiortc.contrib.media import MediaPlayer

from api.services.ffmpeg_launcher import start_ffmpeg, wait_for_rtp_packets

router = APIRouter()

ICE_SERVERS = [
    RTCIceServer(urls="stun:stun.l.google.com:19302"),
    RTCIceServer(
        urls="turn:192.168.1.128:3478",
        username="user",
        credential="pass"
    )
]

active_peer = None

@router.post("/webrtc/offer")
async def webrtc_offer(request: Request):
    body = await request.json()
    offer = RTCSessionDescription(sdp=body["sdp"], type=body["type"])

    config = RTCConfiguration(iceServers=ICE_SERVERS)
    pc = RTCPeerConnection(configuration=config)

    global active_peer
    if active_peer is not None:
        return JSONResponse(status_code=409, content={"detail": "Stream déjà en cours"})
    active_peer = pc

    port = start_ffmpeg()
    wait_for_rtp_packets(port)
    player = MediaPlayer(f"udp://127.0.0.1:{port + 1}", format="rtp")

    track = player.video
    transceiver = pc.addTransceiver(track, direction="sendonly")
    transceiver.setCodecPreferences(RTCRtpSender.getCapabilities("video").codecs)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    @pc.on("connectionstatechange")
    async def on_state_change():
        print("📡 Connexion state:", pc.connectionState)
        if pc.connectionState in ("closed", "failed", "disconnected"):
            global active_peer
            active_peer = None

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }
