from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import Comment

async def create_comment(session: AsyncSession, text: str, user_id: int, photo_id: int) -> Comment:
    """Creates a new comment in the database.

    Args:
        session (AsyncSession): The database session.
        text (str): The text of the comment.
        user_id (int): The ID of the user who made the comment.
        photo_id (int): The ID of the photo the comment is about.

    Returns:
        Comment: The newly created comment.
    """
    new_comment = Comment(text=text, user_id=user_id, photo_id=photo_id)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment

async def get_comments_by_photo(session: AsyncSession, photo_id: int) -> list[Comment]:
    """Gets all comments for the specified photo.

    Args:
        session (AsyncSession): The database session.
        photo_id (int): The ID of the photo for which to retrieve comments.

    Returns:
        list[Comment]: A list of comments for the specified photo.
    """
    query = select(Comment).where(Comment.photo_id == photo_id)
    result = await session.execute(query)
    return result.scalars().all()

async def update_comment(session: AsyncSession, comment_id: int, new_text: str, user_id: int) -> Comment:
    """Updates the text of a comment if the user is the owner.

    Args:
        session (AsyncSession): The database session.
        comment_id (int): The ID of the comment to update.
        new_text (str): The new text for the comment.
        user_id (int): The ID of the user attempting to update the comment.

    Returns:
        Comment: The updated comment.

    Raises:
        PermissionError: If the user is not the owner of the comment.
    """
    comment = await session.get(Comment, comment_id)
    if comment.user_id != user_id:
        raise PermissionError("You can edit only your own comments")

    comment.text = new_text
    await session.commit()
    await session.refresh(comment)
    return comment

async def delete_comment(session: AsyncSession, comment_id: int):
    """Deletes a comment from the database.

    Args:
        session (AsyncSession): The database session.
        comment_id (int): The ID of the comment to delete.
    """
    comment = await session.get(Comment, comment_id)
    if comment:
        await session.delete(comment)
        await session.commit()