from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class PhotoValidationSchema(BaseModel):
    image: str
    description: str
    rating: Optional[float]


class PhotosSchemaResponse(PhotoValidationSchema):
    id: int = 1
    image: str
    description: str
    rating: Optional[float]
    user_id: int
    created_at: datetime
    updated_at: datetime


class PhotoBase(BaseModel):
    description: Optional[str] = None
    tags: List[str] = []


class PhotoCreate(PhotoBase):
    image: str


class PhotoResponse(PhotoCreate):
    id: int
    user_id: int
    tags : List[str]