from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.database.db import get_db
from src.entity.models import User
from src.schemas.comments import CommentCreate, CommentResponse, CommentUpdate
from src.repository.comments import create_comment, get_comments_by_photo, update_comment, delete_comment
from src.services.auth import auth_service
from src.services.role import roles_required

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, summary="Create a comment", description="Creates a new comment for a given photo.")
async def add_comment(
    comment: CommentCreate,
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Creates a new comment for a given photo.

    Args:
        comment (CommentCreate): The comment to be created.
        user_id (int): The ID of the user who is making the comment.
        session (AsyncSession): The database session.

    Returns:
        CommentResponse: The newly created comment.
    """
    return await create_comment(session, comment.text, user_id, comment.photo_id)


@router.get("/{photo_id}", response_model=List[CommentResponse], summary="Get all comments for a photo", description="Retrieve all comments associated with a photo by its ID.")
async def get_photo_comments(
    photo_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Retrieve all comments associated with a photo by its ID.

    Args:
        photo_id (int): The ID of the photo for which to retrieve comments.

    Returns:
        List[CommentResponse]: A list of comments associated with the specified photo.
    """
    return await get_comments_by_photo(session, photo_id)


@router.put("/{comment_id}", response_model=CommentResponse, summary="Edit a comment", description="Updates a comment by its ID.")
async def edit_comment(
    comment_id: int,
    comment: CommentUpdate,
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Updates a comment by its ID.

    Args:
        comment_id (int): The ID of the comment to update.
        comment (CommentUpdate): The new comment text.
        user_id (int): The ID of the user who made the comment.
        session (AsyncSession): The database session.

    Raises:
        HTTPException: If the user is not the owner of the comment.
    """
    try:
        return await update_comment(session, comment_id, comment.text, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{comment_id}", summary="Delete a comment", description="Deletes a comment by its ID.")
@roles_required(["admin", "moderator"])
async def remove_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Deletes a comment by its ID.

    Args:
        comment_id (int): The ID of the comment to delete.
        session (AsyncSession): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A message indicating that the comment was deleted.
    """
    await delete_comment(session, comment_id)
    return {"detail": "Comment deleted"}