from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.db import get_db
from src.entity.models import Tag
from src.schemas.tag import TagResponse
from typing import List

router_tag = APIRouter(prefix="/tags", tags=["tags"])

@router_tag.get("/tags", response_model=List[TagResponse])
async def get_tags(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Tag))
    tags = result.scalars().all()
    return [TagResponse(name=tag.name) for tag in tags]

@router_tag.delete("/tags/{tag_name}", status_code=204)
async def delete_tag(tag_name: str, session: AsyncSession = Depends(get_db)):
    tag = await session.execute(select(Tag).where(Tag.name == tag_name))
    tag = tag.scalars().first()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await session.delete(tag)
    await session.commit()

@router_tag.post("/tags", response_model=TagResponse)
async def create_or_get_tag(tag_name: str, session: AsyncSession = Depends(get_db)):
    # Проверка, существует ли уже такой тег
    result = await session.execute(select(Tag).where(Tag.name == tag_name))
    tag = result.scalars().first()

    if not tag:
        # Если тега нет, создаем новый
        tag = Tag(name=tag_name)
        session.add(tag)
        await session.commit()
        await session.refresh(tag)

    return TagResponse(name=tag.name)