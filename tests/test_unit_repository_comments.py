from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Comment
from src.repository.comments import create_comment, get_comments_by_photo, update_comment, delete_comment


class TestCreateComment(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.comment_id = 1
        self.text = "This is a test comment"
        self.user_id = 1
        self.photo_id = 10
        self.other_user_id = 2
        self.new_text = "Updated comment text"
        self.mock_comment = Comment(
            id=self.comment_id,
            text=self.text,
            user_id=self.user_id,
            photo_id=self.photo_id
        )
        self.mock_comments = [
            Comment(id=1, text="Comment 1", user_id=1, photo_id=self.photo_id),
            Comment(id=2, text="Comment 2", user_id=2, photo_id=self.photo_id),
        ]

    async def test_create_comment_success(self):
        # Mock session behavior
        self.session.refresh = AsyncMock()
        self.session.commit = AsyncMock()

        def mock_add(instance):
            # Simulate adding an object to the database
            instance.id = 1

        self.session.add.side_effect = mock_add

        # Call the function
        result = await create_comment(self.session, self.text, self.user_id, self.photo_id)

        # Assertions
        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(result)

        self.assertEqual(result.text, self.text)
        self.assertEqual(result.user_id, self.user_id)
        self.assertEqual(result.photo_id, self.photo_id)
        self.assertEqual(result.id, 1)

    async def test_get_comments_by_photo_success(self):
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = self.mock_comments
        self.session.execute.return_value = mock_result

        # Call the function
        result = await get_comments_by_photo(self.session, self.photo_id)

        # Assertions
        # self.session.execute.assert_awaited_once_with(select(Comment).where(Comment.photo_id == self.photo_id))
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        expected_query = select(Comment).where(Comment.photo_id == self.photo_id)
        self.assertEqual(str(executed_query), str(expected_query))
        self.assertEqual(result, self.mock_comments)
        self.assertEqual(len(result), len(self.mock_comments))
        self.assertEqual(result[0].text, "Comment 1")
        self.assertEqual(result[1].text, "Comment 2")

    async def test_get_comments_by_photo_no_comments(self):
        # Mock empty database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.session.execute.return_value = mock_result

        # Call the function
        result = await get_comments_by_photo(self.session, self.photo_id)

        # Assertions
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        expected_query = select(Comment).where(Comment.photo_id == self.photo_id)
        self.assertEqual(str(executed_query), str(expected_query))
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    async def test_update_comment_success(self):
        # Mock database response for session.get
        self.session.get.return_value = self.mock_comment

        # Call the function
        result = await update_comment(self.session, self.comment_id, self.new_text, self.user_id)

        # Assertions
        self.session.get.assert_awaited_once_with(Comment, self.comment_id)
        self.assertEqual(result.text, self.new_text)
        self.assertEqual(result.user_id, self.user_id)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(result)

    async def test_update_comment_permission_error(self):
        # Mock database response for session.get
        self.session.get.return_value = self.mock_comment

        # Call the function and expect PermissionError
        with self.assertRaises(PermissionError) as context:
            await update_comment(self.session, self.comment_id, self.new_text, self.other_user_id)

        # Assertions
        self.session.get.assert_awaited_once_with(Comment, self.comment_id)
        self.assertEqual(str(context.exception), "You can edit only your own comments")
        self.session.commit.assert_not_awaited()
        self.session.refresh.assert_not_awaited()

    async def test_delete_comment_success(self):
        # Mock database response for session.get
        self.session.get.return_value = self.mock_comment

        # Call the function
        await delete_comment(self.session, self.comment_id)

        # Assertions
        self.session.get.assert_awaited_once_with(Comment, self.comment_id)
        self.session.delete.assert_awaited_once_with(self.mock_comment)
        self.session.commit.assert_awaited_once()

    async def test_delete_comment_not_found(self):
        # Mock database response for session.get (None means comment not found)
        self.session.get.return_value = None

        # Call the function
        await delete_comment(self.session, self.comment_id)

        # Assertions
        self.session.get.assert_awaited_once_with(Comment, self.comment_id)
        self.session.delete.assert_not_awaited()
        self.session.commit.assert_not_awaited()