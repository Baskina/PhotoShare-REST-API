from pydantic import BaseModel
from typing import Optional


class PhotoTransferResponse(BaseModel):
    id: int
    image: str
    link_url: str
    link_qr: Optional[str] = None
    photo_id: int

    class Config:
        from_attributes = True
