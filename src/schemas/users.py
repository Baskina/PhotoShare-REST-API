from pydantic import BaseModel, EmailStr, Field, PastDatetime


# validation Schemas

class UserValidationSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    hash: str = Field(min_length=8, max_length=8)
    role: str = "user"


class UserValidationSchemaResponse(BaseModel):
    id: int = 1
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: str = "user"
    avatar: str

    # refresh_token: str
    # created_at
    # updated_at

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
