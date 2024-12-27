from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from typing import List,Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Photo,Tag
from src.services.auth import auth_service
from src.database.db import get_db
from src.services.cloudinary import upload_image_to_cloudinary,delete_image_from_cloudinary,generate_transformed_image_url
from src.schemas.photo import PhotoResponse,PhotoCreate
from sqlalchemy import select
import logging


router = APIRouter(prefix="/photo", tags=["photo"])



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@router.post("/", response_model=PhotoResponse)
async def create_photo(
        description: Optional[str] = Form(None),
        tags: List[str] = Form(...),
        file: UploadFile = File(...),
        session: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):

    tags = tags[0].split(",") if isinstance(tags, list) else tags.split(",")


    if len(tags) > 5:
        raise HTTPException(status_code=400, detail="You can add up to 5 tags.")


    tags = list(set(tags))


    image_url, public_id = await upload_image_to_cloudinary(file)


    new_photo = Photo(
        image=public_id,
        description=description,
        user_id=user.id,
    )


    session.add(new_photo)

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
        "image": image_url
    }


@router.delete("/{photo_id}", status_code=204)
async def delete_photo(
        photo_id: int,
        user=Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db)
):
    photo_result = await session.execute(select(Photo).where(Photo.id == photo_id))
    photo = photo_result.scalars().first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if photo.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")


    delete_image_from_cloudinary(photo.image)


    await session.delete(photo)
    await session.commit()


@router.get("/{photo_id}/transform")
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
    return {"transformed_url": transformed_url}