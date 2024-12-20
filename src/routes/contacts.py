from fastapi import APIRouter, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.contacts import (
    ContactValidationSchemaResponse,
    ContactValidationSchema,
)
from src.database.db import get_db

from src.repository import (
    contacts as repositories_contacts,
)
from src.services.auth import (
    auth_service,
)

routerContacts = APIRouter(prefix="/contacts", tags=["contacts"])


@routerContacts.get(
    "/",
    response_model=list[ContactValidationSchemaResponse],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_all_contacts(
    limit: int = Query(default=10, ge=10, le=10),
    offset: int = Query(default=0, ge=0),
    name: str = Query(default=None),
    last_name: str = Query(default=None),
    email: str = Query(default=None),
    find_BD: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves a list of contacts based on the provided filters.

    Args:
        limit (int): The maximum number of contacts to return. Defaults to 10.
        offset (int): The offset from which to start returning contacts. Defaults to 0.
        name (str): The name of the contact to filter by. Defaults to None.
        last_name (str): The last name of the contact to filter by. Defaults to None.
        email (str): The email of the contact to filter by. Defaults to None.
        find_BD (bool): A flag to filter contacts by upcoming birthdays. Defaults to False.
        db (AsyncSession): The database session.
        current_user (User): The user who owns the contacts.

    Returns:
        list[ContactValidationSchemaResponse]: A list of contacts that match the provided filters.
    """

    contacts = await repositories_contacts.read_all_contacts(
        limit, offset, name, last_name, email, find_BD, db, current_user.id
    )
    return contacts


@routerContacts.get(
    "/{contact_id}",
    response_model=ContactValidationSchemaResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def read_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieves a contact from the database based on the provided contact ID.

    Args:
        contact_id (int): The ID of the contact to retrieve. Defaults to 1.
        db (AsyncSession): The database session.
        current_user (User): The user who owns the contact.

    Returns:
        ContactValidationSchemaResponse: The retrieved contact.
    """
    contact = await repositories_contacts.read_contact(contact_id, db, current_user.id)

    return contact


@routerContacts.post(
    "/",
    response_model=ContactValidationSchemaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def add_contact(
    body: ContactValidationSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Creates a new contact in the database.

    Args:
        body (ContactValidationSchema): The contact information to be added.
        db (AsyncSession): The database session.
        current_user (User): The user who owns the contact.

    Returns:
        ContactValidationSchemaResponse: The newly created contact.
    """
    contact = await repositories_contacts.add_contact(body, db, current_user.id)

    return contact


@routerContacts.put(
    "/{contact_id}", dependencies=[Depends(RateLimiter(times=1, seconds=20))]
)
async def update_contact(
    body: ContactValidationSchemaResponse,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Updates a contact in the database based on the provided contact ID.

    Args:
        body (ContactValidationSchemaResponse): The updated contact information.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session.
        current_user (User): The user who owns the contact.

    Returns:
        ContactValidationSchemaResponse: The updated contact.
    """
    contact = await repositories_contacts.update_contact(
        body, contact_id, db, current_user.id
    )

    return contact


@routerContacts.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Deletes a contact from the database based on the provided contact ID.

    Args:
        contact_id (int): The ID of the contact to delete. Defaults to 1.
        db (AsyncSession): The database session.
        current_user (User): The user who owns the contact.

    Returns:
        None
    """
    await repositories_contacts.delete_contact(contact_id, db, current_user.id)
