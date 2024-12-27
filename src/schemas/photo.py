from pydantic import BaseModel
from typing import List, Optional

class PhotoBase(BaseModel):
    description: Optional[str] = None
    tags: List[str] = []


class PhotoCreate(PhotoBase):
    image: str


class PhotoResponse(PhotoCreate):
    id: int
    user_id: int
