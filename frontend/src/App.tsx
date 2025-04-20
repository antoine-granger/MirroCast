import './App.css'
import {JSX, useEffect, useState} from 'react'

type VideoResponse = {
    videos: string[]
}

function App(): JSX.Element {
    const [videos, setVideos] = useState<string[]>([])
    const [url, setUrl] = useState<string>('')
    const [loading, setLoading] = useState<boolean>(false)

    const backendHost = window.location.hostname;
    const backendPort = "8000";
    const backendUrl = `http://${backendHost}:${backendPort}`;

    const [statusMessage, setStatusMessage] = useState<string>("")
    const [progress, setProgress] = useState<number>(0)

    const refreshVideos = () => {
        fetch(`${backendUrl}/videos`)
            .then(res => res.json())
            .then((data: VideoResponse) => setVideos(data.videos))
    }

    useEffect(() => {
        fetch(`${backendUrl}/videos`)
            .then(res => res.json())
            .then((data: VideoResponse) => setVideos(data.videos))
    }, [])

    const handleDownload = async (): Promise<void> => {
        if (!url) return

        setLoading(true)
        setStatusMessage("Téléchargement en cours...")
        setProgress(0)

        let intervalId: NodeJS.Timeout

        // Lancer la progression visuelle en parallèle
        intervalId = setInterval(() => {
            setProgress((oldProgress) => {
                if (oldProgress >= 100) {
                    clearInterval(intervalId)
                    setStatusMessage("Téléchargement terminé ! 🎉")
                    setTimeout(() => {
                        refreshVideos()
                        setStatusMessage("")
                        setProgress(0)
                    }, 2000)
                    return 100
                }
                return oldProgress + 5
            })
        }, 300)

        // Appeler le backend (on ne fait rien à la fin ici)
        await fetch(`${backendUrl}/download`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({url}),
        }).finally(() => setLoading(false))
    }

    return (
        <div style={{textAlign: "center", padding: "2rem"}}>
            <img src="/MirroCast-2.png" width={150}/>
            <h1>MirroCast</h1>

            <button onClick={refreshVideos} style={{marginBottom: "1rem"}}>
                🔄 Rafraîchir les vidéos
            </button>

            {statusMessage && (
                <div style={{marginTop: "1rem", color: "#333"}}>
                    {statusMessage}
                </div>
            )}

            {loading && (
                <div style={{marginTop: "1rem", width: "60%", margin: "auto"}}>
                    <div className="progress-bar-container">
                        <div
                            className="progress-bar-fill"
                            style={{width: `${progress}%`}}
                        />
                    </div>
                    <p>{progress}%</p>
                </div>
            )}

            <div style={{margin: "2rem"}}>
                <input
                    type="text"
                    placeholder="Coller une URL YouTube"
                    value={url}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUrl(e.target.value)}
                    style={{
                        width: "400px",
                        padding: "0.5rem",
                        border: "1px solid #ccc",
                        borderRadius: "4px"
                    }}
                />
                <button
                    onClick={handleDownload}
                    disabled={loading}
                    style={{
                        marginLeft: "1rem",
                        padding: "0.5rem 1rem",
                        cursor: "pointer"
                    }}
                >
                    {loading ? "Téléchargement..." : "Télécharger"}
                </button>
                {loading && (
                    <div className="spinner"/>
                )}
            </div>

            <h2>Vidéos disponibles</h2>
            <ul>
                {videos.map((video) => {
                    const name = video.replace(/\.[^/.]+$/, "") // Pour enlever .mp4
                    return (
                        <li key={video}>
                            <video
                                src={`${backendUrl}/media/${encodeURIComponent(video)}`}
                                poster={`${backendUrl}/media/${encodeURIComponent(name)}.jpg`}
                                width="600"
                                style={{borderRadius: "6px", marginBottom: "1rem"}}
                                controls
                            />
                            <p>{video}</p>
                        </li>
                    )
                })}
            </ul>
        </div>
    )
}

export default App