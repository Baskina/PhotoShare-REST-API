from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import (
    UserValidationSchema,
)


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a user from the database based on the provided email address.

    Args:
        email (str): The email address of the user to retrieve.
        db (AsyncSession): The database session. Defaults to Depends(get_db).

    Returns:
        User or None: The retrieved user, or None if no user is found.
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)

    user = user.scalar_one_or_none()
    return user

async def get_user_by_id(user_id: str, session: AsyncSession):
    query = select(User).where(User.id == user_id)

    user = await session.execute(query)

    user = user.scalar_one_or_none()
    return user

async def count_users(db: AsyncSession) -> int:
    """
    Returns the number of users in the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        int: The number of users in the database.
    """
    stmt = select(User.id)
    result = await db.execute(stmt)
    return len(result.all()) 

async def create_user(body: UserValidationSchema, db: AsyncSession = Depends(get_db)):
    """
    Creates a new user in the database.

    Args:
        body (UserValidationSchema): The user's information to be added.
        db (AsyncSession): The database session. Defaults to Depends(get_db).

    Returns:
        User: The newly created user.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Updates the refresh token of a user in the database.

    Args:
        user (User): The user whose refresh token is to be updated.
        token (str | None): The new refresh token.
        db (AsyncSession): The database session.

    Returns:
        None
    """
    user.refresh_token = token
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Updates the avatar URL of a user in the database.

    Args:
        email (str): The email address of the user to update.
        url (str | None): The new avatar URL.
        db (AsyncSession): The database session.

    Returns:
        User: The user with the updated avatar URL.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url

    await db.commit()
    await db.refresh(user)
    return user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirms a user's email address by updating their confirmation status in the database.

    Args:
        email (str): The email address of the user to confirm.
        db (AsyncSession): The database session.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
