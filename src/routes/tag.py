from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.db import get_db
from src.entity.models import User,Tag, Photo, photo_tag_association
from src.schemas.tag import TagResponse
from typing import List
from src.services.auth import auth_service
router_tag = APIRouter(prefix="/tags", tags=["tags"])

@router_tag.get("/", response_model=List[TagResponse])
async def get_tags(photo_id: int, session: AsyncSession = Depends(get_db),user=Depends(auth_service.get_current_user)):
    """
        Retrieve a list of tags associated with a specific photo.

        Args:
            photo_id (int): The ID of the photo for which to retrieve tags.
            session (AsyncSession): The database session.

        Returns:
            List[TagResponse]: A list of tags associated with the specified photo.
    """
    result = await session.execute(
        select(Tag).join(photo_tag_association).where(photo_tag_association.c.photo_id == photo_id)
    )
    tags = result.scalars().all()
    return [TagResponse(name=tag.name) for tag in tags]

@router_tag.delete("/{tag_name}", status_code=204)
async def delete_tag(tag_name: str, session: AsyncSession = Depends(get_db),user=Depends(auth_service.get_current_user)):
    """
        Delete a tag by its name, including its associations with photos.

        Args:
            tag_name (str): The name of the tag to delete.
            session (AsyncSession): The database session.

        Raises:
            HTTPException: If the tag is not found (404).

        Returns:
            dict: A message confirming the successful deletion of the tag and its associations.
    """
    tag_result = await session.execute(select(Tag).where(Tag.name == tag_name))
    tag = tag_result.scalars().first()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await session.execute(
        photo_tag_association.delete().where(photo_tag_association.c.tag_id == tag.id)
    )

    await session.delete(tag)
    await session.commit()

    return {"message": f"Tag '{tag_name}' and its associations deleted successfully"}

@router_tag.post("/{photo_id}/add-tags", status_code=200)
async def add_tags_to_photo_route(
    photo_id: int,
    tag_names: List[str],
    session: AsyncSession = Depends(get_db),
    user=Depends(auth_service.get_current_user)
):
    """
    Add a list of tags to a specific photo.

    Args:
        photo_id (int): The ID of the photo to which tags will be added.
        tag_names (List[str]): A list of tag names to add to the photo.
        session (AsyncSession): The database session.

    Raises:
        HTTPException: If the photo is not found (404).
        HTTPException: If adding the tags exceeds the limit of 5 tags (400).

    Returns:
        dict: A message confirming the successful addition of the tags to the photo.
    """
    tag_names = list(set(tag_names))

    photo_result = await session.execute(select(Photo).where(Photo.id == photo_id))
    photo = photo_result.scalars().first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    existing_tags = await session.execute(
        select(photo_tag_association).where(photo_tag_association.c.photo_id == photo_id)
    )
    existing_tags_count = existing_tags.rowcount

    if existing_tags_count + len(tag_names) > 5:
        raise HTTPException(
            status_code=400,
            detail=f"You can only have up to 5 tags. Current: {existing_tags_count}, Adding: {len(tag_names)}"
        )

    for tag_name in tag_names:
        tag_result = await session.execute(select(Tag).where(Tag.name == tag_name))
        tag = tag_result.scalars().first()

        if not tag:
            tag = Tag(name=tag_name)
            session.add(tag)
            await session.flush()

        existing_association = await session.execute(
            select(photo_tag_association).where(
                photo_tag_association.c.photo_id == photo_id,
                photo_tag_association.c.tag_id == tag.id
            )
        )
        if existing_association.scalars().first():
            continue

        await session.execute(
            photo_tag_association.insert().values(photo_id=photo_id, tag_id=tag.id)
        )

    await session.commit()
    return {"message": f"Tags {tag_names} added to photo {photo_id} successfully"}


