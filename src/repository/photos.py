import datetime
from typing import Tuple, Any, List

import qrcode
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from src.entity.models import Photo, User, photo_tag_association, Tag, Like, PhotoTransfer
from src.services import cloudinary
from src.services.rating_calculation import rating_calculation


async def add_photo(url: str, description: str, db: AsyncSession, user_id: int) -> Photo:
    """Adds a new photo to the database.

    Args:
        url (str): The URL of the photo.
        description (str): The description of the photo.
        db (AsyncSession): The database session.
        user_id (int): The ID of the user who added the photo.

    Returns:
        Photo: The newly added photo.
    """
    photo = Photo(image=url, description=description, created_at=datetime.datetime.now(),
                  updated_at=datetime.datetime.now(), rating=0, user_id=user_id)
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def delete_photo(photo_id: int, db: AsyncSession):
    """Deletes a photo from the database.

    Args:
        photo_id (int): The ID of the photo to delete.
        db (AsyncSession): The database session.

    Returns:
        Photo: The deleted photo.
    """
    stmt = select(Photo).filter_by(id=photo_id)
    # stmt = stmt.filter_by(user_id=user_id)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        await db.delete(photo)
        await db.commit()
    return photo


async def update_photo(
        photo_id: int, description: str, db: AsyncSession) -> Photo:
    """Updates description of the photo in the database.

    Args:
        photo_id (int): The ID of the photo to update.
        description (str): The new description of the photo.
        db (AsyncSession): The database session.

    Returns:
        Photo: The updated photo.
    """
    stmt = select(Photo).filter_by(id=photo_id)
    # stmt = stmt.filter_by(user_id=user_id)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if photo:
        photo.description = description
        photo.updated_at = datetime.datetime.now()
        await db.commit()
        await db.refresh(photo)
    return photo


async def read_photo(photo_id: int, db: AsyncSession) -> Photo | None:
    """Gets a photo from the database.

    Args:
        photo_id (int): The ID of the photo to get.
        db (AsyncSession): The database session.

    Returns:
        Photo | None: The photo if found, otherwise None.
    """
    stmt = select(Photo).filter_by(id=photo_id)
    # stmt = stmt.filter_by(user_id=user_id)
    photo = await db.execute(stmt)
    return photo.scalar_one_or_none()


async def read_all_photos(
        limit: int,
        offset: int,
        db: AsyncSession,
        user_id: int,
) -> list[Photo]:
    """Gets all photos for the current user from the database.

    Args:
        limit (int): The maximum number of photos to return.
        offset (int): The offset from which to start returning photos.
        db (AsyncSession): The database session.
        user_id (int): The ID of the user to filter photos by.

    Returns:
        list[Photo]: A list of photos that belong to the user.
    """
    stmt = select(Photo).offset(offset).limit(limit)
    stmt = stmt.filter_by(user_id=user_id)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def read_all_photos_all_users(
        limit: int,
        offset: int,
        db: AsyncSession
) -> list[Photo]:
    """
    Retrieve all photos for all users.

    **Parameters**

    * `limit`: The maximum number of photos to return
    * `offset`: The offset from which to start returning photos
    * `db`: An asynchronous database session

    **Returns**

    * A list of `Photo` objects, each representing a photo.

    **Description**

    This function executes a SQL query to retrieve a list of all photos for all users, with pagination. The query uses the provided `limit` and `offset` parameters to control the number of results returned.

    **Note**

    This function does not perform any authentication or authorization checks. It is intended to be used internally by the application.
    """
    stmt = select(Photo).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def search_photos(
        limit: int,
        offset: int,
        keyword: str,
        tag_id: int,
        min_rating: int,
        max_rating: int,
        min_created_at: datetime,
        max_created_at: datetime,
        db: AsyncSession,
) -> list[Photo]:
    """
    Searches photos in the database by keyword, tag ID, rating, and creation date.

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

    Returns:
        list[Photo]: A list of photos that match the search criteria.
    """
    stmt = (
        select(Photo)
        .join(photo_tag_association, Photo.id == photo_tag_association.c.photo_id)
        .join(Tag, Tag.id == photo_tag_association.c.tag_id)
        .offset(offset)
        .limit(limit)
    )
    if keyword:
        stmt = stmt.filter(Photo.description.ilike(f"%{keyword}%"))
    if tag_id:
        stmt = stmt.filter(photo_tag_association.c.tag_id == tag_id)
    if min_rating:
        stmt = stmt.filter(or_(Photo.rating >= min_rating, Photo.rating.is_(None)))
    if max_rating:
        stmt = stmt.filter(or_(Photo.rating <= max_rating, Photo.rating.is_(None)))
    if min_created_at:
        stmt = stmt.filter(Photo.created_at >= min_created_at)
    if max_created_at:
        stmt = stmt.filter(Photo.created_at <= max_created_at)
    stmt = stmt.order_by(Photo.rating.desc())
    stmt = stmt.order_by(Photo.created_at.desc())
    photos = await db.execute(stmt)
    return photos.scalars().all()



async def search_photos_by_user(limit: int, offset: int, user_id: int, name: str, db: AsyncSession) -> list[Photo]:
    """
    Searches for photos by user ID and name.

    Args:
        limit (int): The maximum number of photos to return.
        offset (int): The offset from which to start returning photos.
        user_id (int): The ID of the user to search for. If 0, search all users.
        name (str): The part of the username to search for.
        db (AsyncSession): The database session.

    Returns:
        list[Photo]: A list of photos that match the criteria.
    """
    stmt = select(Photo).join(User, Photo.user_id == User.id).offset(offset).limit(limit)
    if user_id != 0:
        stmt = stmt.filter(Photo.user_id == user_id)
    if name:
        stmt = stmt.filter(User.username.ilike(f"%{name}%"))
    stmt = stmt.order_by(Photo.user_id)
    photos = await db.execute(stmt)
    return photos.scalars().all()


async def rate_photo(photo_id: int, like_value: int, user_id: int, db: AsyncSession) -> Photo | None:
    """
    Rates a photo.

    Args:
        photo_id (int): The ID of the photo to rate.
        like_value (int): The value to rate the photo with.
        user_id (int): The ID of the user who is rating the photo.
        db (AsyncSession): The database session.

    Raises:
        HTTPException: If the user has already rated the photo.

    Returns:
        Photo | None: The rated photo if it exists, otherwise None.
    """
    stmt = select(Like).filter_by(photo_id=photo_id, user_id=user_id)
    like = await db.execute(stmt)
    like = like.scalar_one_or_none()
    if like:
        raise HTTPException(status_code=400, detail="You have already rated this photo")
    like = Like(like_value=like_value, photo_id=photo_id, user_id=user_id)
    db.add(like)
    await db.commit()
    await db.refresh(like)

    return await rating_calculation(photo_id, db)


async def view_rating_photo(photo_id: int, db: AsyncSession) -> list[dict]:
    """
    Gets all likes of a photo.

    Args:
        photo_id (int): The ID of the photo.
        db (AsyncSession): The database session.

    Raises:
        HTTPException: If the photo does not exist.

    Returns:
        list[dict]: A list of dictionaries containing the like information. Each dictionary has the following keys:
            id (int): The ID of the like.
            like_value (int): The value of the like.
            user_id (int): The ID of the user who liked the photo.
            username (str): The username of the user who liked the photo.
    """
    stmt = (
        select(
            Photo.id,
            Photo.image,
            Photo.description,
            Photo.rating,
            Like.id.label("like_id"),
            Like.like_value,
            User.id.label("user_id"),
            User.username,
        )
        .join(Like, Photo.id == Like.photo_id)
        .join(User, User.id == Like.user_id)
        .where(Photo.id == photo_id)
    )
    result = await db.execute(stmt)
    photos_rating = [dict(row) for row in result.mappings().all()]
    if not photos_rating:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photos_rating


async def delete_like_of_photo(like_id: int, db: AsyncSession) -> Photo | None:
    """
    Deletes a like of a photo and recalculates the photo's rating.

    Args:
        like_id (int): The ID of the like to delete.
        db (AsyncSession): The database session.

    Raises:
        HTTPException: If the like does not exist.

    Returns:
        Photo | None: The photo if it exists, otherwise None.
    """
    stmt = select(Like).filter_by(id=like_id)
    like = await db.execute(stmt)
    like = like.scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    photo_id = like.photo_id
    await db.delete(like)
    await db.commit()

    return await rating_calculation(photo_id, db)


async def save_transform_photo(photo_id: int, image: str, transformed_url: str,
                               db: AsyncSession) -> PhotoTransfer | None:
    """
    Saves a transformed photo to the database.

    This function creates a new entry in the `PhotoTransfer` table, associating
    the transformed photo with the original photo and storing the transformed image URL.

    Args:
        photo_id (int): The ID of the original photo associated with the transformation.
        image (str): The URL or path of the transformed image.
        transformed_url (str): The URL of the transformed image.
        db (AsyncSession): The database session used for database operations.

    Returns:
        PhotoTransfer | None: The created `PhotoTransfer` record if successful, otherwise None.

    Raises:
        HTTPException: If there is an issue with the database operation.
    """
    photo_transfer = PhotoTransfer(
        image=image,
        link_url=transformed_url,
        photo_id=photo_id,
    )
    db.add(photo_transfer)
    await db.commit()

    return photo_transfer


async def generate_and_save_qr(photo_transfer: PhotoTransfer, qr_url: str, db: AsyncSession) -> PhotoTransfer | None:
    """
    Generates a QR code URL for a transformed photo's link and saves it to the database.

    This function generates a QR code URL for the `link_url` of a `PhotoTransfer` record
    and saves it in the `link_qr` field.

    Args:
        qr_url: The base URL of the QR code
        photo_transfer (PhotoTransfer): The ID of the `PhotoTransfer` record to update.
        base_url (str): The base URL of the server where the QR code will be hosted.
        db (AsyncSession): The database session used for database operations.

    Returns:
        PhotoTransfer | None: The updated `PhotoTransfer` record if successful, otherwise None.

    Raises:
        HTTPException: If the `PhotoTransfer` record with the given ID is not found.
    """

    photo_transfer.link_qr = qr_url
    db.add(photo_transfer)
    await db.commit()
    await db.refresh(photo_transfer)

    return photo_transfer
