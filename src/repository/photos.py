import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Photo, User, photo_tag_association, Tag


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


async def read_all_photos(limit: int, offset: int, db: AsyncSession, user_id: int):
    stmt = select(Photo).offset(offset).limit(limit)
    if user_id != 0:
        stmt = stmt.filter_by(user_id=user_id)
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
        stmt = stmt.filter(Photo.rating >= min_rating)
    if max_rating:
        stmt = stmt.filter(Photo.rating <= max_rating)
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