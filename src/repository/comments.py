from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import Comment

async def create_comment(session: AsyncSession, text: str, user_id: int, photo_id: int):
    new_comment = Comment(text=text, user_id=user_id, photo_id=photo_id)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment

async def get_comments_by_photo(session: AsyncSession, photo_id: int):
    query = select(Comment).where(Comment.photo_id == photo_id)
    result = await session.execute(query)
    return result.scalars().all()

async def update_comment(session: AsyncSession, comment_id: int, new_text: str, user_id: int):
    comment = await session.get(Comment, comment_id)
    if comment.user_id == user_id:
        comment.text = new_text
        await session.commit()
        await session.refresh(comment)
        return comment
    raise PermissionError("You can edit only your own comments")

async def delete_comment(session: AsyncSession, comment_id: int):
    comment = await session.get(Comment, comment_id)
    if comment:
        await session.delete(comment)
        await session.commit()