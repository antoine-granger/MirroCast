from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, Response
import os

router = APIRouter()
VIDEO_DIR = "media"

@router.get("/stream/{filename}")
async def stream_video(request: Request, filename: str):
    file_path = os.path.join(VIDEO_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Vidéo introuvable")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("range")

    if range_header:
        range_value = range_header.strip().lower().replace("bytes=", "")
        range_start, range_end = range_value.split("-")
        range_start = int(range_start)
        range_end = int(range_end) if range_end else file_size - 1
        content_length = range_end - range_start + 1

        def iter_file():
            with open(file_path, "rb") as f:
                f.seek(range_start)
                yield f.read(content_length)

        return StreamingResponse(
            iter_file(),
            status_code=206,
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {range_start}-{range_end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
            },
        )
    else:
        # Pas d'en-tête Range → envoie tout
        return Response(
            content=open(file_path, "rb").read(),
            media_type="video/mp4"
        )
