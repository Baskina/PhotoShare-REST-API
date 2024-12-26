import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Photo


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
