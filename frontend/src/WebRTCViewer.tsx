import {useRef, useState} from "react";

const useLogger = () => {
    const [logs, setLogs] = useState<string[]>([])

    const log = (...args: any[]) => {
        const message = args.map(a => typeof a === "object" ? JSON.stringify(a) : String(a)).join(" ")
        setLogs(prev => [...prev.slice(-15), message])
        console.log(...args)
    }

    return {logs, log}
}

const WebRTCViewer = ({backendUrl}: { backendUrl: string }) => {
    const videoRef = useRef<HTMLVideoElement | null>(null)
    const pcRef = useRef<RTCPeerConnection | null>(null)
    const [active, setActive] = useState(false)

    const {logs, log} = useLogger()

    const handleFullscreen = () => {
        const video = videoRef.current
        if (video) {
            if (document.fullscreenElement) {
                document.exitFullscreen()
            } else {
                video.requestFullscreen().catch((err) => {
                    console.error("❌ Plein écran échoué", err)
                })
            }
        }
    }

    const startWebRTC = async () => {
        if (active) {
            console.log("🛑 Arrêt du partage WebRTC")
            pcRef.current?.close()
            pcRef.current = null
            if (videoRef.current) {
                videoRef.current.srcObject = null
            }
            setActive(false)
            return
        }

        const pc = new RTCPeerConnection({
            iceServers: [
                {urls: "stun:stun.l.google.com:19302"},
                {
                    urls: "turn:192.168.1.128:3478",
                    username: "webrtc",
                    credential: "mirrocast",
                },
            ],
        });


        pc.onconnectionstatechange = () => {
            console.error("📡 WebRTC state:", pc.connectionState)
        }
        pc.oniceconnectionstatechange = () => {
            log("❄️ ICE state:", pc.iceConnectionState);
        };
        pc.onicecandidate = (event) => {
            if (event.candidate) {
                console.log("🧊 Candidate envoyée :", event.candidate.candidate);
            } else {
                console.log("✅ Tous les candidats ICE envoyés.");
            }
        };
        pcRef.current = pc
        pc.addTransceiver("video", {direction: "recvonly"})

        pc.ontrack = (event) => {
            console.log("📺 WebRTC track received", event.streams[0])
            const video = videoRef.current
            if (video) {
                video.srcObject = event.streams[0]
                console.log("🎥 Flux attaché, tentative de lecture...")

                setTimeout(() => {
                    video.play().then(() => {
                        console.log("▶️ Lecture démarrée")
                    }).catch((err) => {
                        console.error("❌ Lecture refusée", err)
                    })
                }, 500)
            }
        }

        const offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        const res = await fetch(`${backendUrl}/webrtc/offer`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(pc.localDescription)
        })

        const answer = await res.json()
        await pc.setRemoteDescription(answer)
        setActive(true)
    }

    const forcePlay = () => {
        const video = videoRef.current
        if (video) {
            const tracks = (video.srcObject as MediaStream)?.getVideoTracks() ?? []
            console.log("🎥 Nombre de tracks vidéo :", tracks.length)
            console.log("🎥 Track info :", tracks[0])

            video.play().then(() => {
                console.log("▶️ Lecture manuelle OK")
            }).catch((err) => {
                console.error("❌ Lecture manuelle échouée", err)
            })
        }
    }

    return (
        <div style={{marginTop: "2rem", textAlign: "center"}}>
            <button onClick={startWebRTC}>
                {active ? "🛑 Stopper WebRTC" : "▶️ Activer WebRTC"}
            </button>
            <button onClick={handleFullscreen} style={{marginLeft: "1rem"}}>
                ⛶ Plein écran
            </button>

            <div style={{marginTop: "1rem"}}>
                <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    onClick={forcePlay}
                    onDoubleClick={handleFullscreen}
                    style={{
                        width: "100%",
                        maxWidth: "800px",
                        borderRadius: "8px",
                        background: "#000"
                    }}
                />
            </div>

            <button onClick={forcePlay} style={{marginTop: "1rem"}}>
                🎬 Lancer la lecture
            </button>

            {/* 🧪 Console visible */}
            <div style={{
                marginTop: "2rem",
                textAlign: "left",
                padding: "1rem",
                background: "#eee",
                fontSize: "0.8rem",
                maxWidth: "800px",
                marginInline: "auto"
            }}>
                <h3>🧪 Logs client</h3>
                <pre>{logs.map((line, i) => <div key={i}>{line}</div>)}</pre>
            </div>
        </div>
    )
}

export default WebRTCViewer
