from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    text: str
    photo_id: int


class CommentResponse(BaseModel):
    id: int
    text: str
    photo_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentUpdate(BaseModel):
    text: str