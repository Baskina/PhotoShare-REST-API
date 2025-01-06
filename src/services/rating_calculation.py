import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Photo, Like

async def rating_calculation(photo_id: int, db: AsyncSession) -> Photo | None:
    """
    Calculates the rating of a photo and updates the photo in the database.

    Args:
        photo_id (int): The ID of the photo.
        db (AsyncSession): The database session.

    Returns:
        Photo | None: The updated photo if it exists, otherwise None.
    """
    stmt = select(Like.like_value).filter_by(photo_id=photo_id)
    result = await db.execute(stmt)
    like_value = result.scalars().all()
    if len(like_value) == 0:
        rating = None
    else:
        rating = round(sum(like_value) / len(like_value), 2)
    stmt = select(Photo).filter_by(id=photo_id)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        photo.rating = rating
        photo.updated_at = datetime.datetime.now()
        await db.commit()
        await db.refresh(photo)
    return photo