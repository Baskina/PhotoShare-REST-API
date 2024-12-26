import uuid
from urllib.parse import urlparse, unquote

import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, status, Path, HTTPException, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User, Photo
from src.schemas.photos import PhotosSchemaResponse
from src.database.db import get_db

from src.repository import photos as repositories_photos
from src.services.auth import auth_service

routerPhotos = APIRouter(prefix="/photos", tags=["photos"])


@routerPhotos.post(
    "/",
    response_model=PhotosSchemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new photo with its description",
    description="Adds a new photo to the database",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def add_photo(
        discription: str,
        file: UploadFile = File(description="The image file to be uploaded"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> Photo:
    """
    Adds a new photo to the database.

    Args:
        discription (str): The description of the photo.
        file (UploadFile, optional): The image file to be uploaded. Defaults to File.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user, obtained through authentication services.
        Defaults to Depends(auth_service.get_current_user).

    Returns:
        PhotosSchemaResponse: The newly created photo.
    """
    public_id = f"Digital workspace/{current_user.email}/{uuid.uuid4().hex}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=False)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=1000, height=1000, crop="fill", version=res.get("version")
    )
    photo = await repositories_photos.add_photo(
        res_url, discription, db, current_user.id)

    return photo


@routerPhotos.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a photo",
    description="Deletes a photo from the database",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_photo(
        photo_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Deletes a photo from the database and from Cloudinary.

    Args:
        photo_id (int): The ID of the photo to delete.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Raises:
        HTTPException: If the photo does not exist, or the user does not have permission to delete it.
    """
    res = await repositories_photos.read_photo(photo_id, db)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if current_user.role == "admin" or res.user_id == current_user.id:
        image_to_delete = res.image
        parsed_url = urlparse(image_to_delete)
        path_parts = parsed_url.path.split('/')
        url_image_to_delete = '/'.join(path_parts[6:])
        decoded_public_id = unquote(url_image_to_delete)
        result = cloudinary.uploader.destroy(public_id=decoded_public_id,
                                             invalidate=True)
        if result["result"] == "ok":
            await repositories_photos.delete_photo(photo_id, db)
        elif result["result"] == "not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found in Cloudinary")
        else:
            raise Exception(result["result"])
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")


@routerPhotos.put(
    "/{photo_id}",
    response_model=PhotosSchemaResponse,
    summary="Update description of a photo by ID",
    description="Updates description of a photo in the database by its ID",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_photo(
        photo_id: int,
        discription: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Updates description of a photo in the database by its ID.

    Args:
        photo_id (int): The ID of the photo to update.
        discription (str): The new description of the photo.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Raises:
        HTTPException: If the photo does not exist, or the user does not have permission to update it.

    Returns:
        PhotosSchemaResponse: The updated photo.
    """
    res = await repositories_photos.read_photo(photo_id, db)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if current_user.role == "admin" or res.user_id == current_user.id:
        update_photo = await repositories_photos.update_photo(photo_id, discription, db)
        return update_photo
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")


@routerPhotos.get(
    "/{photo_id}",
    response_model=PhotosSchemaResponse,
    summary="Retrieve a photo by ID",
    description="Gets a photo from the database by its ID",
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_photo(
        photo_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Gets a photo from the database by its ID.

    Args:
        photo_id (int): The ID of the photo to retrieve.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Raises:
        HTTPException: If the photo does not exist, or the user does not have permission to read it.

    Returns:
        PhotosSchemaResponse: The retrieved photo.
    """
    photo = await repositories_photos.read_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if photo.user_id == current_user.id or current_user.role == "admin":
        return photo
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")
