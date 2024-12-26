from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:567234@localhost:5432/fast_db"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_CLOUD_NAME: str = "ddkhc0hci"
    CLOUDINARY_API_KEY: int = 337619357218213
    CLOUDINARY_API_SECRET: str = "secret"

    MAIL_USERNAME: str = "email@gmail.com"
    MAIL_PASSWORD: str = "passw888"
    MAIL_FROM: str = "email@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v


config = Settings()
