from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.database.db import get_db
from src.schemas.comments import CommentCreate, CommentResponse, CommentUpdate
from src.repository.comments import create_comment, get_comments_by_photo, update_comment, delete_comment

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse)
async def add_comment(
    comment: CommentCreate, 
    user_id: int, 
    session: AsyncSession = Depends(get_db)
):
    """
    Adds a comment to the database.
    """
    return await create_comment(session, comment.text, user_id, comment.photo_id)

@router.get("/{photo_id}", response_model=List[CommentResponse])
async def get_photo_comments(
    photo_id: int, 
    session: AsyncSession = Depends(get_db)
):
    """
    Отримує список коментарів до світлини.
    """
    return await get_comments_by_photo(session, photo_id)

@router.put("/{comment_id}", response_model=CommentResponse)
async def edit_comment(
    comment_id: int, 
    comment: CommentUpdate, 
    user_id: int, 
    session: AsyncSession = Depends(get_db)
):
    """
    Retrieves a list of comments for a photo.
    """
    try:
        return await update_comment(session, comment_id, comment.text, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{comment_id}")
async def remove_comment(
    comment_id: int, 
    session: AsyncSession = Depends(get_db)
):
    """
    Deletes a comment (only for administrator or moderator).
    """
    await delete_comment(session, comment_id)
    return {"detail": "Comment deleted"}