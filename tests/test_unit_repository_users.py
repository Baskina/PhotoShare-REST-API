from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import User
from src.repository.users import (get_user_by_email, count_users, create_user,
                                  update_token, update_avatar_url, confirmed_email)
from src.schemas.users import UserValidationSchema


class TestGetUserByEmail(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.email = "test@example.com"
        self.mock_user = User(id=1, username="testuser", email=self.email,
                              hash="hashed_password", avatar="https://example.com/old-avatar.jpg")
        self.mock_user_ids = [1, 2, 3]
        self.mock_user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "hash": "hashedpa",
        }
        self.mock_avatar_url = "https://www.gravatar.com/avatar/testhash"
        self.new_avatar_url = "https://example.com/new-avatar.jpg"


    async def test_get_user_by_email_success(self):
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.mock_user
        self.session.execute.return_value = mock_result

        # Call the function
        result = await get_user_by_email(self.email, self.session)

        # Assertions
        #self.session.execute.assert_awaited_once_with(select(User).filter_by(email=self.email))
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        expected_query = select(User).where(User.email == self.email)
        self.assertEqual(str(executed_query), str(expected_query))
        self.assertEqual(result, self.mock_user)

    async def test_get_user_by_email_not_found(self):
        # Mock database response (None means user not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result

        # Call the function
        result = await get_user_by_email(self.email, self.session)

        # Assertions
        # self.session.execute.assert_awaited_once_with(select(User).filter_by(email=self.email))
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        expected_query = select(User).where(User.email == self.email)
        self.assertEqual(str(executed_query), str(expected_query))
        self.assertIsNone(result)


    async def test_count_users_success(self):
        # Mock database response
        mock_result = MagicMock()
        mock_result.all.return_value = [(user_id,) for user_id in self.mock_user_ids]
        self.session.execute.return_value = mock_result

        # Call the function
        result = await count_users(self.session)

        # Assertions
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        expected_query = select(User.id)
        self.assertEqual(str(executed_query), str(expected_query))
        self.assertEqual(result, len(self.mock_user_ids))

    async def test_count_users_empty(self):
        # Mock database response for no users
        mock_result = MagicMock()
        mock_result.all.return_value = []
        self.session.execute.return_value = mock_result

        # Call the function
        result = await count_users(self.session)

        # Assertions
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        expected_query = select(User.id)
        self.assertEqual(str(executed_query), str(expected_query))
        self.assertEqual(result, 0)


    @patch("src.repository.users.Gravatar")
    async def test_create_user_success(self, mock_gravatar):
        # Mock Gravatar response
        mock_gravatar_instance = mock_gravatar.return_value
        mock_gravatar_instance.get_image.return_value = self.mock_avatar_url

        # Prepare user schema
        body = UserValidationSchema(**self.mock_user_data)

        # Call the function
        result = await create_user(body, self.session)

        # Assertions
        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(result)
        self.assertEqual(result.email, self.mock_user_data["email"])
        self.assertEqual(result.username, self.mock_user_data["username"])
        self.assertEqual(result.avatar, self.mock_avatar_url)

    @patch("src.repository.users.Gravatar")
    async def test_create_user_gravatar_failure(self, mock_gravatar):
        # Mock Gravatar to raise an exception
        mock_gravatar.return_value.get_image.side_effect = Exception("Gravatar error")

        # Prepare user schema
        body = UserValidationSchema(**self.mock_user_data)

        # Call the function
        result = await create_user(body, self.session)

        # Assertions
        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(result)
        self.assertEqual(result.email, self.mock_user_data["email"])
        self.assertEqual(result.username, self.mock_user_data["username"])
        self.assertIsNone(result.avatar)

    async def test_create_user_session_commit_failure(self):
        # Prepare user schema
        body = UserValidationSchema(**self.mock_user_data)

        # Mock session.commit to raise an exception
        self.session.commit.side_effect = Exception("Database error")

        # Call the function and expect an exception
        with self.assertRaises(Exception) as context:
            await create_user(body, self.session)

        self.assertEqual(str(context.exception), "Database error")
        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()


    @patch("src.repository.users.get_user_by_email")
    async def test_update_avatar_url_success(self, mock_get_user_by_email):
        # Mock get_user_by_email
        mock_get_user_by_email.return_value = self.mock_user

        # Call the function
        updated_user = await update_avatar_url(self.email, self.new_avatar_url, self.session)

        # Assertions
        mock_get_user_by_email.assert_awaited_once_with(self.email, self.session)
        self.assertEqual(updated_user.avatar, self.new_avatar_url)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(self.mock_user)

    @patch("src.repository.users.get_user_by_email")
    async def test_update_avatar_url_user_not_found(self, mock_get_user_by_email):
        # Mock get_user_by_email to return None
        mock_get_user_by_email.return_value = None

        # Call the function and expect an exception
        with self.assertRaises(AttributeError):  # Or another exception depending on your error handling
            await update_avatar_url(self.email, self.new_avatar_url, self.session)

        mock_get_user_by_email.assert_awaited_once_with(self.email, self.session)
        self.session.commit.assert_not_awaited()
        self.session.refresh.assert_not_awaited()

    @patch("src.repository.users.get_user_by_email")
    async def test_update_avatar_url_remove_avatar(self, mock_get_user_by_email):
        # Mock get_user_by_email
        mock_get_user_by_email.return_value = self.mock_user

        # Call the function with None for the avatar URL
        updated_user = await update_avatar_url(self.email, None, self.session)

        # Assertions
        mock_get_user_by_email.assert_awaited_once_with(self.email, self.session)
        self.assertIsNone(updated_user.avatar)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(self.mock_user)


    @patch("src.repository.users.get_user_by_email")
    async def test_confirmed_email_success(self, mock_get_user_by_email):
        # Мокаем возврат пользователя
        mock_get_user_by_email.return_value = self.mock_user

        # Вызываем тестируемую функцию
        await confirmed_email(self.email, self.session)

        # Проверяем вызов get_user_by_email
        mock_get_user_by_email.assert_awaited_once_with(self.email, self.session)

        # Проверяем обновление confirmed
        self.assertTrue(self.mock_user.confirmed)

        # Проверяем вызовы session
        self.session.commit.assert_awaited_once()

    @patch("src.repository.users.get_user_by_email")
    async def test_confirmed_email_user_not_found(self, mock_get_user_by_email):
        # Мокаем отсутствие пользователя
        mock_get_user_by_email.return_value = None

        # Проверяем, что функция выбрасывает исключение
        with self.assertRaises(AttributeError):  # Если user = None, то user.confirmed вызовет AttributeError
            await confirmed_email(self.email, self.session)

        # Проверяем вызов get_user_by_email
        mock_get_user_by_email.assert_awaited_once_with(self.email, self.session)

        # Проверяем, что commit не вызывается
        self.session.commit.assert_not_awaited()
