import {useEffect, useState} from 'react'

function App() {
    const [videos, setVideos] = useState<string[]>([])
    const [url, setUrl] = useState('')
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        fetch("http://localhost:8000/videos")
            .then(res => res.json())
            .then(data => setVideos(data.videos))
    }, [])

    const handleDownload = async () => {
        if (!url) return;

        setLoading(true)
        await fetch("http://localhost:8000/download", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({url})
        })
            .then((res) => res.json())
            .then(() => {
                alert("Téléchargement lancé ! Reviens dans quelques secondes.")
                setUrl("")
                setTimeout(() => window.location.reload(), 7000) // relancer la liste après un délai
            })
            .finally(() => setLoading(false))
    }

    return (
        <div style={{textAlign: "center", padding: "2rem"}}>
            <img src="/MirroCast.png" width={150}/>
            <h1>MirroCast</h1>

            <div style={{margin: "2rem"}}>
                <input
                    type="text"
                    placeholder="Coller une URL YouTube"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
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
            </div>

            <h2>Vidéos disponibles</h2>
            <ul>
                {videos.map((video) => {
                    const name = video.replace(/\.[^/.]+$/, "") // remove extension
                    return (
                        <li key={video}>
                            <img
                                src={`http://localhost:8000/media/${name}.jpg`}
                                alt="miniature"
                                width="300"
                                style={{marginBottom: "1rem", borderRadius: "6px"}}
                                onError={(e) => (e.target.style.display = "none")} // au cas où pas de miniature
                            />
                            <video
                                src={`http://localhost:8000/media/${video}`}
                                controls
                                width="600"
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