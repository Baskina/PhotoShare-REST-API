import uuid
from datetime import datetime
from urllib.parse import urlparse, unquote
from typing import List
import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, status, Path, HTTPException, UploadFile, File, Query, Form
from fastapi_limiter.depends import RateLimiter

from src.entity.models import User, Photo, Tag, PhotoTransfer
from src.schemas.photo_transfer import PhotoTransferResponse
from src.schemas.photos import PhotosSchemaResponse, PhotoValidationSchema, PhotoResponse, PhotoCreate

from src.repository import photos as repositories_photos

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import auth_service
from src.database.db import get_db
from src.services.cloudinary import upload_image_to_cloudinary, generate_transformed_image_url, upload_qr_to_cloudinary
from src.services.role import roles_required

routerPhotos = APIRouter(prefix="/photos", tags=["photos"])

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@routerPhotos.post("/", response_model=PhotoResponse)
async def create_photo(
        description: str = Form(...),
        tags: List[str] = Form(...),
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
       Creates a new photo and uploads it to Cloudinary. The photo is then associated with tags and saved in the database.

       Args:
           description (str): A description of the photo.
           tags (List[str]): A list of tags to associate with the photo. Maximum of 5 tags are allowed.
           file (UploadFile): The file to upload as the photo.
           session (AsyncSession): The database session used to interact with the database.
           user (User): The currently authenticated user making the request.

       Raises:
           HTTPException: If more than 5 tags are provided.

       Returns:
           dict: A dictionary containing the following fields:
               - id (int): The ID of the newly created photo.
               - user_id (int): The ID of the user who uploaded the photo.
               - description (str): The description of the photo.
               - tags (List[str]): A list of tags associated with the photo.
               - image (str): The URL of the uploaded image in Cloudinary.
       """
    tags = tags[0].split(",") if isinstance(tags, list) else tags.split(",")

    if len(tags) > 5:
        raise HTTPException(status_code=400, detail="You can add up to 5 tags.")

    tags = list(set(tags))
    image_url, public_id = await upload_image_to_cloudinary(file)

    new_photo = Photo(
        image=image_url,
        description=description,
        user_id=user.id,
    )

    session.add(new_photo)
    if len("".join(tags)) > 0:
        for tag_name in tags:
            tag_result = await session.execute(select(Tag).where(Tag.name == tag_name))
            tag = tag_result.scalars().first()

            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)

            new_photo.photo_tags.append(tag)

    await session.commit()
    await session.refresh(new_photo)

    return {
        "id": new_photo.id,
        "user_id": new_photo.user_id,
        "description": new_photo.description,
        "tags": tags,
        "image": image_url,
    }

@routerPhotos.get(
    "/all",
    response_model=list[PhotosSchemaResponse],
#    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
    summary="Retrieve all photos",
    description="Gets a list of All photos",
)
async def read_photos_all_users(
        limit: int = Query(default=10, ge=0, le=50, description="The maximum number of photos to return"),
        offset: int = Query(default=0, ge=0, description="The offset from which to start returning photos"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
) -> list[PhotosSchemaResponse]:
    """
    Retrieve all photos.

    Returns a list of photos for all users, with optional pagination.

    **Query Parameters**

    * `limit`: The maximum number of photos to return (default: 10, range: 0-50)
    * `offset`: The offset from which to start returning photos (default: 0)

    **Response**

    * A list of `PhotosSchemaResponse` objects, each representing a photo.

    **Description**

    This endpoint retrieves a list of all photos for all users. The response can be paginated using the `limit` and `offset` query parameters. If a photo does not have a description, a default description of "No description provided" is used.

    **Authentication**

    This endpoint requires authentication. The `current_user` is retrieved using the `auth_service.get_current_user` dependency.

    **Database**

    This endpoint uses the `get_db` dependency to retrieve an asynchronous database session.
    """
    photos = await repositories_photos.read_all_photos_all_users(limit=limit, offset=offset, db=db)
    for photo in photos:
        if not photo.description:
            photo.description = "No description provided"
    return photos


@routerPhotos.get(
    "/search",
    response_model=list[PhotosSchemaResponse],
    summary="Retrieve all photos by keyword and tag ID",
    description="Gets all photos from the database by keyword and tag ID",
#    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def search_photos(
        limit: int = Query(default=10, ge=0, le=50, description="The maximum number of photos to return"),
        offset: int = Query(default=0, ge=0, description="The offset from which to start returning photos"),
        keyword: str = Query(default=None, description="The keyword to search for in the description"),
        tag_id: int = Query(default=None, ge=0, description="The ID of the tag to search for"),
        min_rating: int = Query(default=0, ge=0, le=5, description="The minimum rating to search for"),
        max_rating: int = Query(default=5, ge=0, le=5, description="The maximum rating to search for"),
        min_created_at: datetime = Query(default="2020-01-01T00:00:00",
                                         description="The minimum creation date to search for"),
        max_created_at: datetime = Query(default=datetime.now(),
                                         description="The maximum creation date to search for"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Gets all photos from the database by keyword and tag ID.

    Args:
        limit (int): The maximum number of photos to return.
        offset (int): The offset from which to start returning photos.
        keyword (str): The keyword to search for in the description.
        tag_id (int): The ID of the tag to search for.
        min_rating (int): The minimum rating to search for.
        max_rating (int): The maximum rating to search for.
        min_created_at (datetime): The minimum creation date to search for.
        max_created_at (datetime): The maximum creation date to search for.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Returns:
        list[PhotosSchemaResponse]: A list of photos that match the search criteria.

    Raises:
        HTTPException: If no photos are found.
    """
    photos = await repositories_photos.search_photos(limit, offset, keyword, tag_id, min_rating, max_rating,
                                                     min_created_at,
                                                     max_created_at, db)
    if not photos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photos not found")
    return photos


@routerPhotos.get(
    "/search/{user_id}",
    response_model=list[PhotosSchemaResponse],
    summary="Retrieve all photos by user ID",
    description="Gets all photos from the database by user ID",
)
# @roles_required(["admin", "moderator"])
async def search_photos_by_user(
        limit: int = Query(default=10, ge=0, le=50, description="The maximum number of photos to return"),
        offset: int = Query(default=0, ge=0, description="The offset from which to start returning photos"),
        user_id: int = Path(ge=0, description="User ID to search. If '0' - a list of photos of all users is displayed"),
        name: str = Query(default=None, description="Part of username to search for"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> list[PhotosSchemaResponse]:
    """
    Gets all photos from the database by user ID.

    Args:
        limit (int): The maximum number of photos to return.
        offset (int): The offset from which to start returning photos.
        user_id (int): User ID to search. If '0' - a list of photos of all users is displayed.
        name (str): The name of the user to search for.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user, obtained through authentication services.

    Returns:
        list[PhotosSchemaResponse]: A list of photos that match the search criteria.

    Raises:
        HTTPException: If no photos are found.
    """
    photos = await repositories_photos.search_photos_by_user(limit, offset, user_id, name, db)
    if not photos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photos not found")
    return photos


@routerPhotos.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a photo",
    description="Deletes a photo from the database",
#    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
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

        print(f"Parsed URL path: {parsed_url.path}")
        path_parts = parsed_url.path.split('/')

        if len(path_parts) >= 1:
            public_id = path_parts[-1].split('.')[0]
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format for public_id")

        try:
            result = cloudinary.uploader.destroy(public_id=public_id, invalidate=True)
            if result["result"] == "ok":
                await repositories_photos.delete_photo(photo_id, db)
            elif result["result"] == "not found":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found in Cloudinary")
            else:
                raise Exception(f"Error deleting photo from Cloudinary: {result['result']}")
        except cloudinary.exceptions.Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Cloudinary error: {str(e)}")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")


@routerPhotos.put(
    "/{photo_id}",
    response_model=PhotosSchemaResponse,
    summary="Update description of a photo by ID",
    description="Updates description of a photo in the database by its ID",
#    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_photo(
        photo_id: int,
        description: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Updates description of a photo in the database by its ID.

    Args:
        photo_id (int): The ID of the photo to update.
        description (str): The new description of the photo.
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
        update_photo = await repositories_photos.update_photo(photo_id, description, db)
        return update_photo
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission")


@routerPhotos.get(
    "/{photo_id}",
    response_model=PhotosSchemaResponse,
    summary="Retrieve a photo by ID",
    description="Gets a photo from the database by its ID",
#    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
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
    return photo


@routerPhotos.get(
    "/",
    response_model=list[PhotosSchemaResponse],
#    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
    summary="Retrieve all photos for the current user",
    description="Gets a list of photos for the current user from the database",
)
async def read_photos_of_current_user(
        limit: int = Query(default=10, ge=0, le=50, description="The maximum number of photos to return"),
        offset: int = Query(default=0, ge=0, description="The offset from which to start returning photos"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> list[PhotosSchemaResponse]:
    """
    Retrieves a list of photos for the current user.

    Args:
        limit (int): The maximum number of photos to return.
        offset (int): The offset from which to start returning photos.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        list[PhotosSchemaResponse]: A list of photos that belong to the current user.
    """
    photos = await repositories_photos.read_all_photos(limit=limit, offset=offset, db=db, user_id=current_user.id)
    for photo in photos:
        if not photo.description:
            photo.description = "No description provided"
    return photos


@routerPhotos.get("/{photo_id}/transform")
async def transform_photo(
        photo_id: int,
        width: int = 300,
        height: int = 300,
        crop: str = "fill",
        angle: int = 0,
        effect: str = None,
        quality: int = None,
        format: str = None,
        user=Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
        Transforms a photo by applying various modifications such as resizing, cropping, rotating, and adding effects.

        Args:
            photo_id (int): The ID of the photo to transform.
            width (int): The width of the transformed image (default is 300).
            height (int): The height of the transformed image (default is 300).
            crop (str): The crop mode (default is 'fill'). Other options can include 'scale', 'fit', etc.
            angle (int): The angle to rotate the image (default is 0).
            effect (str, optional): The name of the effect to apply (e.g., 'grayscale'). If not provided, no effect is applied.
            quality (int, optional): The quality of the transformed image (default is None).
            format (str, optional): The format to convert the image to (e.g., 'jpeg'). If not provided, no conversion is applied.
            user (User): The currently authenticated user.
            session (AsyncSession): The database session for querying the photo.

        Raises:
            HTTPException:
                - 404: If the photo with the given ID is not found.
                - 403: If the current user does not have permission to transform the photo.

        Returns:
            dict: A dictionary containing the transformed image URL.
                - transformed_url (str): The URL of the transformed image.
        """
    photo_result = await session.execute(select(Photo).where(Photo.id == photo_id))
    photo = photo_result.scalars().first()

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    if photo.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    transformations = {"width": width, "height": height, "crop": crop}
    if angle:
        transformations["angle"] = angle
    if effect:
        transformations["effect"] = effect
    if quality:
        transformations["quality"] = quality
    if format:
        transformations["format"] = format

    transformed_url = generate_transformed_image_url(photo.image.split("/")[-1].split(".")[0], transformations)

    photo = await repositories_photos.save_transform_photo(photo_id, photo.image.split("/")[-1].split(".")[0],
                                                           transformed_url, session)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transformed photo not save")

    return {"transformed_url": transformed_url}


@routerPhotos.put(
    "/{photo_id}/rating",
    response_model=PhotoValidationSchema,
    summary="Rate a photo",
    description="Rates a photo with a value between 1 and 5",
#    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def rate_photo(
        photo_id: int = Path(ge=1, description="The ID of the photo to rate"),
        like_value: int = Query(ge=1, le=5, description="The value to rate the photo with"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """Rates a photo with a value between 1 and 5.

    Args:
        photo_id (int): The ID of the photo to rate.
        like_value (int): The value to rate the photo with.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException:
            - 404: If the photo with the given ID is not found.
            - 400: If the rating value is not between 1 and 5.
            - 400: If the current user is the same as the photo's user.

    Returns:
        PhotosSchemaResponse: The rated photo.
    """
    photo = await repositories_photos.read_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if current_user.id == photo.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't rate your own photo")
    await repositories_photos.rate_photo(photo_id, like_value, current_user.id, db)
    return photo


@routerPhotos.get(
    "/{photo_id}/rating",
    response_model=list[dict],
    summary="View likes of a photo",
    description="Retrieves all likes of a photo by its ID",
)
@roles_required(["admin", "moderator"])
async def view_rating_photo(
        photo_id: int = Path(ge=1, description="The ID of the photo to view likes"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves all likes of a photo by its ID.

    Args:
        photo_id (int): The ID of the photo to view likes.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        list[dict]: A list of dictionaries containing the like information.
    """
    result = await repositories_photos.view_rating_photo(photo_id, db)
    return result


@routerPhotos.delete(
    "/rating/{like_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a like of a photo",
    description="Deletes a like of a photo by its ID",
)
@roles_required(["admin", "moderator"])
async def delete_like_of_photo(
        like_id: int = Path(ge=1, description="The ID of the like to delete"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
) -> None:
    """
    Deletes a like of a photo by its ID.

    Args:
        like_id (int): The ID of the like to delete.
        db (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        None
    """
    return await repositories_photos.delete_like_of_photo(like_id, db)


@routerPhotos.post(
    "/create-qr-code",
    response_model=PhotoTransferResponse,
    summary="Create URL and QR code for a photo",
)
@roles_required(["admin", "moderator"])
async def create_qr_code(
        photo_transfer_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user),
):
    """
    Generates a QR code URL for a transformed photo's link and saves it to the database.

    Args:
    current_user (User): The currently authenticated user.
    photo_transfer_id (int): The ID of the PhotoTransfer record to update.
    db (AsyncSession): The database session used for database operations.
    base_url (str): The base URL of the server where the QR code will be hosted.

    Returns:
        PhotoTransfer | None: The updated PhotoTransfer record if successful, otherwise None.

    Raises:
        HTTPException: If the PhotoTransfer record with the given ID is not found.
    """
    photo_transfer_result = await db.execute(
        select(PhotoTransfer).where(PhotoTransfer.id == photo_transfer_id)
    )
    photo_transfer = photo_transfer_result.scalars().first()

    if not photo_transfer:
        raise HTTPException(status_code=404, detail="Photo record not found")

    if not photo_transfer.link_qr:
        link_qr = await upload_qr_to_cloudinary(photo_transfer.link_url)
        photo_transfer = await repositories_photos.generate_and_save_qr(photo_transfer, link_qr, db)

    return photo_transfer
