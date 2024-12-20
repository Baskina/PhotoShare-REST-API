import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User
from src.schemas.users import UserValidationSchema
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_avatar_url,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        user = User(username="test", email="test@mail.com", hash='pass8888')
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(email="test@mail.com", db=self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserValidationSchema(username="test", email="test@mail.com", hash='pass8888')
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_avatar_url(self):
        user = User(username="test", email="test@mail.com", hash='pass8888', avatar='old_url')
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user

        result = await update_avatar_url(email="test@mail.com", url="new_url", db=self.session)
        self.assertEqual(result.email, user.email)
        self.assertEqual(result.avatar, 'new_url')


if __name__ == '__main__':
    unittest.main()
