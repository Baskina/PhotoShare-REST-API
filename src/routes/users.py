import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, status, Path, Query, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User

from src.database.db import get_db

from src.schemas.users import (
    UserValidationSchemaResponse,
)
from src.services.auth import (
    auth_service,
)
from src.conf.config import config
from src.repository import (
    users as repository_users,
)


routerUsers = APIRouter(prefix="/users", tags=["users"])

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@routerUsers.get(
    "/me",
    response_model=UserValidationSchemaResponse,
    #dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves the currently authenticated user.

    Args:
        current_user (User): The currently authenticated user, obtained through authentication services.

    Returns:
        User: The currently authenticated user.
    """
    return current_user

@routerUsers.get(
    "/{user_id}",
    response_model=UserValidationSchemaResponse
)
async def get_user(user_id: int, session: AsyncSession = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves a user by their ID.

        Args:
        - user_id (int): The ID of the user to retrieve.
        - session (AsyncSession): The database session. Defaults to the current database session.
        - current_user (User): The currently authenticated user. Defaults to the current authenticated user.

        Returns:
        - User: The retrieved user.

        Raises:
        - [Insert any potential exceptions that may be raised]
    """
    user = await repository_users.get_user_by_id(user_id, session)

    return user

@routerUsers.patch(
    response_model=UserValidationSchemaResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
    path="/me/avatar",
)
async def get_current_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates the avatar of the currently authenticated user.

    Args:
        file (UploadFile): The file to be uploaded as the new avatar.
        current_user (User): The currently authenticated user, obtained through authentication services.
        db (AsyncSession): The database session.

    Returns:
        User: The user with the updated avatar URL.
    """
    public_id = f"Web16/{current_user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )

    user = await repository_users.update_avatar_url(current_user.email, res_url, db)

    return user
