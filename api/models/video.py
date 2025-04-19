from pydantic import BaseModel

class VideoRequest(BaseModel):
    url: str