import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.entity.models import Contact
from src.schemas.contacts import (
    ContactValidationSchemaResponse,
    ContactValidationSchema,
)


def has_birthday_next_days(sa_col, next_days: int = 0):
    """
    Checks if a contact has a birthday within the specified number of next days.

    Args:
        sa_col: A SQLAlchemy column object representing the contact's birth date.
        next_days (int, optional): The number of days to check for upcoming birthdays. Defaults to 0.

    Returns:
        A SQLAlchemy expression evaluating to True if the contact has a birthday within the specified number of next days, False otherwise.
    """
    return age_years_at(sa_col, next_days) > age_years_at(sa_col)


def age_years_at(sa_col, next_days: int = 0):
    """
    Calculates the age in years at a given date.

    Args:
        sa_col: A SQLAlchemy column object representing the date.
        next_days (int, optional): The number of days to add to the date. Defaults to 0.

    Returns:
        A SQLAlchemy expression evaluating to the age in years.
    """
    stmt = func.age(
        (sa_col - sa.func.cast(datetime.timedelta(next_days), sa.Interval))
        if next_days != 0
        else sa_col
    )
    stmt = func.date_part("year", stmt)
    return stmt


async def read_all_contacts(
    limit: int,
    offset: int,
    name: str,
    last_name: str,
    email: str,
    find_BD,
    db: AsyncSession,
    user_id: int,
):
    """
    Retrieves a list of contacts based on the provided filters.

    Args:
        limit (int): The maximum number of contacts to return.
        offset (int): The offset from which to start returning contacts.
        name (str): The name of the contact to filter by.
        last_name (str): The last name of the contact to filter by.
        email (str): The email of the contact to filter by.
        find_BD: A flag to filter contacts by upcoming birthdays.
        db (AsyncSession): The database session.
        user_id (int): The ID of the user who owns the contacts.

    Returns:
        list: A list of contacts that match the provided filters.
    """
    stmt = select(Contact).offset(offset).limit(limit)
    stmt = stmt.filter_by(user_id=user_id)
    if name:
        stmt = stmt.filter_by(name=name)
    if last_name:
        stmt = stmt.filter_by(last_name=last_name)
    if email:
        stmt = stmt.filter_by(email=email)

    if find_BD:
        stmt = stmt.filter(has_birthday_next_days(Contact.birth_date, 7))
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def read_contact(contact_id: int, db: AsyncSession, user_id: int):
    """
    Retrieves a contact from the database based on the provided contact ID and user ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        Contact or None: The retrieved contact, or None if no contact is found.
    """
    stmt = select(Contact).filter_by(id=contact_id)
    stmt = stmt.filter_by(user_id=user_id)
    contact = await db.execute(stmt)

    return contact.scalar_one_or_none()


async def add_contact(body: ContactValidationSchema, db: AsyncSession, user_id):
    """
    Adds a new contact to the database.

    Args:
        body (ContactValidationSchema): The contact information to be added.
        db (AsyncSession): The database session.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        Contact: The newly added contact.
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user_id=user_id)

    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    return contact


async def update_contact(
    body: ContactValidationSchemaResponse, contact_id: int, db: AsyncSession, user_id
):
    """
    Updates a contact in the database based on the provided contact ID and user ID.

    Args:
        body (ContactValidationSchemaResponse): The updated contact information.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session.
        user_id: The ID of the user who owns the contact.

    Returns:
        Contact or None: The updated contact, or None if no contact is found.
    """
    stmt = select(Contact).filter_by(id=contact_id)
    stmt = stmt.filter_by(user_id=user_id)
    result = await db.execute(stmt)

    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.lastName = body.last_name
        contact.email = body.email
        contact.phoneNumber = body.phone_number
        contact.birthDate = body.birth_date
        contact.rest = body.rest
        await db.commit()
        await db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user_id):
    """
    Deletes a contact from the database based on the provided contact ID and user ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session.
        user_id: The ID of the user who owns the contact.

    Returns:
        Contact or None: The deleted contact, or None if no contact is found.
    """
    stmt = select(Contact).filter_by(id=contact_id)
    stmt = stmt.filter_by(user_id=user_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()

    if contact:
        await db.delete(contact)
        await db.commit()

    return contact
