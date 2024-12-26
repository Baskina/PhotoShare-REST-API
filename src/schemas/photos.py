from datetime import datetime
from pydantic import BaseModel


class PhotoValidationSchema(BaseModel):
    image: str
    description: str
    rating: int


class PhotosSchemaResponse(PhotoValidationSchema):
    id: int = 1
    image: str
    description: str
    rating: int
    user_id: int
    created_at: datetime
    updated_at: datetime
