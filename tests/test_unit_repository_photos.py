import time
import unittest
from asyncio import current_task
from types import SimpleNamespace

from fastapi import HTTPException
from unittest.mock import MagicMock, AsyncMock, patch, Mock

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, Photo, photo_tag_association, Tag, Like
from src.schemas.photos import PhotoValidationSchema, PhotosSchemaResponse
from src.repository.photos import (add_photo,
                                   delete_photo,
                                   update_photo,
                                   read_photo,
                                   read_all_photos,
                                   search_photos,
                                   search_photos_by_user,
                                   rate_photo,
                                   view_rating_photo,
                                   delete_like_of_photo
                                   )


class TestPhotos(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user_id = 1
        self.mock_url = "http://example.com/photo.jpg"
        self.mock_description = "Description of test photo"
        self.photo_id = 1
        self.limit = 10
        self.offset = 0
        self.tag_id = 1
        self.min_rating = 3
        self.max_rating = 5
        self.min_created_at = datetime.now() - timedelta(days=30)
        self.max_created_at = datetime.now()
        self.keyword = "user"
        self.like_value = 5
        self.mock_photo = Photo(
            id=self.photo_id,
            image="http://example.com/photo.jpg",
            description="Old description",
            user_id=1,
            rating=4,
            created_at=datetime.now() - timedelta(days=1),
            updated_at=datetime.now(),
        )
        self.mock_photos = [
            Photo(id=1, image="https://example.com/photo1.jpg", description="Photo 1", user_id=self.user_id),
            Photo(id=2, image="https://example.com/photo2.jpg", description="Photo 2", user_id=self.user_id),
        ]


    async def test_add_photo(self):
        result = await add_photo(self.mock_url, self.mock_description, self.session, self.user_id)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(result)

        self.assertIsInstance(result, Photo)
        self.assertEqual(result.image, self.mock_url)
        self.assertEqual(result.description, self.mock_description)
        self.assertEqual(result.user_id, self.user_id)
        self.assertEqual(result.rating, 0)

    async def test_delete_photo_success(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.mock_photo
        self.session.execute.return_value = mock_result
        result = await delete_photo(self.photo_id, self.session)

        self.assertEqual(result, self.mock_photo)
        self.session.execute.assert_awaited_once()
        self.session.delete.assert_awaited_once_with(self.mock_photo)
        self.session.commit.assert_awaited_once()

    async def test_delete_photo_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result
        result = await delete_photo(self.photo_id, self.session)

        self.assertIsNone(result)
        self.session.execute.assert_awaited_once()
        self.session.delete.assert_not_awaited()
        self.session.commit.assert_not_awaited()

    async def test_update_photo_success(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.mock_photo
        self.session.execute.return_value = mock_result
        new_description = "Updated description"
        result = await update_photo(self.photo_id, new_description, self.session)

        self.assertEqual(result.description, new_description)
        #self.assertNotEqual(result.updated_at, self.mock_photo.updated_at)
        self.session.execute.assert_awaited_once()
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(self.mock_photo)

    async def test_update_photo_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result
        new_description = "Updated description"
        result = await update_photo(self.photo_id, new_description, self.session)

        self.assertIsNone(result)
        self.session.execute.assert_awaited_once()
        self.session.commit.assert_not_awaited()
        self.session.refresh.assert_not_awaited()

    async def test_read_photo_success(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.mock_photo
        self.session.execute.return_value = mock_result
        result = await read_photo(self.photo_id, self.session)

        self.assertEqual(result, self.mock_photo)
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(select(Photo).filter_by(id=self.photo_id)))

    async def test_read_photo_not_found(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result
        result = await read_photo(self.photo_id, self.session)

        self.assertIsNone(result)
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(select(Photo).filter_by(id=self.photo_id)))

    async def test_read_all_photos_success(self):
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = self.mock_photos
        self.session.execute.return_value = mock_result
        result = await read_all_photos(self.limit, self.offset, self.session, self.user_id)

        self.assertEqual(result, self.mock_photos)
        expected_query = select(Photo).offset(self.offset).limit(self.limit).filter_by(user_id=self.user_id)
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(expected_query))

    async def test_read_all_photos_empty(self):
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        self.session.execute.return_value = mock_result
        result = await read_all_photos(self.limit, self.offset, self.session, self.user_id)

        self.assertEqual(result, [])
        expected_query = select(Photo).offset(self.offset).limit(self.limit).filter_by(user_id=self.user_id)
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(expected_query))

    async def test_search_photos_by_user_success(self):
        # Мокаем результат выполнения запроса
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = self.mock_photos
        self.session.execute.return_value = mock_result

        self.name = "user"
        result = await search_photos_by_user(self.limit, self.offset, self.user_id, self.name, self.session)

        # Проверяем результат
        self.assertEqual(result, self.mock_photos)

        # Формируем ожидаемый запрос
        expected_query = select(Photo).join(User, Photo.user_id == User.id).offset(self.offset).limit(self.limit)
        if self.user_id != 0:
            expected_query = expected_query.filter(Photo.user_id == self.user_id)
        if self.name:
            expected_query = expected_query.filter(User.username.ilike(f"%{self.name}%"))
        expected_query = expected_query.order_by(Photo.user_id)

        # Проверяем, что метод execute был вызван один раз
        self.session.execute.assert_awaited_once()

        # Получаем фактический выполненный запрос
        executed_query = self.session.execute.call_args[0][0]

        # Сравниваем строковые представления запросов
        self.assertEqual(str(executed_query), str(expected_query))

    async def test_search_photos_by_user_not_found(self):
        # Мокаем результат выполнения запроса (пустой результат)
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        self.session.execute.return_value = mock_result

        self.name = "nonexistent_user"
        result = await search_photos_by_user(self.limit, self.offset, self.user_id, self.name, self.session)

        # Проверяем, что результат пустой
        self.assertEqual(result, [])

        # Формируем ожидаемый запрос
        expected_query = select(Photo).join(User, Photo.user_id == User.id).offset(self.offset).limit(self.limit)
        if self.user_id != 0:
            expected_query = expected_query.filter(Photo.user_id == self.user_id)
        if self.name:
            expected_query = expected_query.filter(User.username.ilike(f"%{self.name}%"))
        expected_query = expected_query.order_by(Photo.user_id)

        # Проверяем, что метод execute был вызван один раз
        self.session.execute.assert_awaited_once()

        # Получаем фактический выполненный запрос
        executed_query = self.session.execute.call_args[0][0]

        # Сравниваем строковые представления запросов
        self.assertEqual(str(executed_query), str(expected_query))


    async def test_search_photos_success(self):
        # Mock the result of the database query
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = self.mock_photos
        self.session.execute.return_value = mock_result

        # Call the function
        result = await search_photos(
            self.limit,
            self.offset,
            self.keyword,
            self.tag_id,
            self.min_rating,
            self.max_rating,
            self.min_created_at,
            self.max_created_at,
            self.session,
        )

        # Assertions
        self.assertEqual(result, self.mock_photos)
        expected_query = (
            select(Photo)
            .join(photo_tag_association, Photo.id == photo_tag_association.c.photo_id)
            .join(Tag, Tag.id == photo_tag_association.c.tag_id)
            .offset(self.offset)
            .limit(self.limit)
            .filter(Photo.description.ilike(f"%{self.keyword}%"))
            .filter(photo_tag_association.c.tag_id == self.tag_id)
            .filter((Photo.rating >= self.min_rating) | (Photo.rating.is_(None)))
            .filter((Photo.rating <= self.max_rating) | (Photo.rating.is_(None)))
            .filter(Photo.created_at >= self.min_created_at)
            .filter(Photo.created_at <= self.max_created_at)
            .order_by(Photo.rating.desc())
            .order_by(Photo.created_at.desc())
        )
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(expected_query))

    async def test_search_photos_no_results(self):
        # Mock the result of the database query
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = []
        self.session.execute.return_value = mock_result

        # Call the function
        result = await search_photos(
            self.limit,
            self.offset,
            self.keyword,
            self.tag_id,
            self.min_rating,
            self.max_rating,
            self.min_created_at,
            self.max_created_at,
            self.session,
        )
        # Assertions
        self.assertEqual(result, [])
        self.session.execute.assert_awaited_once()

    async def test_search_photos_no_filters(self):
        # Test when no filters are provided
        self.keyword = None
        self.tag_id = None
        self.min_rating = None
        self.max_rating = None
        self.min_created_at = None
        self.max_created_at = None

        # Mock the result of the database query
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = self.mock_photos
        self.session.execute.return_value = mock_result

        # Call the function
        result = await search_photos(
            self.limit,
            self.offset,
            self.keyword,
            self.tag_id,
            self.min_rating,
            self.max_rating,
            self.min_created_at,
            self.max_created_at,
            self.session,
        )

        # Assertions
        self.assertEqual(result, self.mock_photos)
        expected_query = (
            select(Photo)
            .join(photo_tag_association, Photo.id == photo_tag_association.c.photo_id)
            .join(Tag, Tag.id == photo_tag_association.c.tag_id)
            .offset(self.offset)
            .limit(self.limit)
            .order_by(Photo.rating.desc())
            .order_by(Photo.created_at.desc())
        )
        self.session.execute.assert_awaited_once()
        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(expected_query))

    @patch("src.repository.photos.rating_calculation")
    async def test_rate_photo_success(self, mock_rating_calculation):
        # Mock database response: No previous like exists
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result

        # Mock rating_calculation
        mock_rating_calculation.return_value = Photo(id=self.photo_id, rating=4.5)

        # Call the function
        result = await rate_photo(self.photo_id, self.like_value, self.user_id, self.session)

        # Assertions
        self.session.execute.assert_awaited_once()
        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()
        mock_rating_calculation.assert_awaited_once_with(self.photo_id, self.session)

        self.assertIsInstance(result, Photo)
        self.assertEqual(result.rating, 4.5)

    async def test_rate_photo_already_rated(self):
        # Mock database response: Like already exists
        mock_like = Like(id=1, like_value=5, photo_id=self.photo_id, user_id=self.user_id)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_like
        self.session.execute.return_value = mock_result

        # Call the function and check for exception
        with self.assertRaises(HTTPException) as context:
            await rate_photo(self.photo_id, self.like_value, self.user_id, self.session)

        self.session.execute.assert_awaited_once()
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "You have already rated this photo")


    async def test_view_rating_photo_success(self):
        self.mock_likes = [
            {
                "id": 1,
                "image": "http://example.com/photo.jpg",
                "description": "Test photo",
                "rating": 4.5,
                "like_id": 101,
                "like_value": 5,
                "user_id": 1,
                "username": "user1",
            },
            {
                "id": 1,
                "image": "http://example.com/photo.jpg",
                "description": "Test photo",
                "rating": 4.5,
                "like_id": 102,
                "like_value": 4,
                "user_id": 2,
                "username": "user2",
            },
        ]
        # Mock database response
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = self.mock_likes
        self.session.execute.return_value = mock_result

        # Call the function
        result = await view_rating_photo(self.photo_id, self.session)

        # Assertions
        self.session.execute.assert_awaited_once()
        self.assertEqual(len(result), len(self.mock_likes))
        self.assertEqual(result[0]["username"], self.mock_likes[0]["username"])
        self.assertEqual(result[1]["like_value"], self.mock_likes[1]["like_value"])


    async def test_view_rating_photo_not_found(self):
        # Mock empty database response
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        self.session.execute.return_value = mock_result

        # Call the function and check for exception
        with self.assertRaises(HTTPException) as context:
            await view_rating_photo(self.photo_id, self.session)

        self.session.execute.assert_awaited_once()
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Photo not found")


    @patch("src.repository.photos.rating_calculation", new_callable=AsyncMock)
    async def test_delete_like_success(self, mock_rating_calculation):
        self.like_id = 1
        self.mock_like = MagicMock(id=self.like_id, photo_id=10)
        self.mock_photo = MagicMock(id=10, rating=4.5)
        # Mock database response for Like
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.mock_like
        self.session.execute.return_value = mock_result

        # Mock rating calculation
        mock_rating_calculation.return_value = self.mock_photo

        # Call the function
        result = await delete_like_of_photo(self.like_id, self.session)

        # Assertions
        like_query = select(Like).filter_by(id=self.like_id)
        executed_query = self.session.execute.call_args[0][0]
        self.assertEqual(str(executed_query), str(like_query))  # Compare SQL strings
        self.session.delete.assert_awaited_once_with(self.mock_like)
        self.session.commit.assert_awaited_once()
        mock_rating_calculation.assert_awaited_once_with(self.mock_like.photo_id, self.session)

        self.assertIsNotNone(result)

    async def test_delete_like_not_found(self):
        self.like_id = 1
        self.mock_like = MagicMock(id=self.like_id, photo_id=10)
        self.mock_photo = MagicMock(id=10, rating=4.5)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result

        # Call the function and expect an exception
        with self.assertRaises(HTTPException) as context:
            await delete_like_of_photo(self.like_id, self.session)

        # Assertions
        self.session.execute.assert_awaited_once()
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Like not found")


if __name__ == '__main__':
    unittest.main()