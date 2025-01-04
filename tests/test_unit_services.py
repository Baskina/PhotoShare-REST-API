import unittest
from asyncio import current_task
from types import SimpleNamespace

from fastapi import HTTPException, UploadFile
from unittest.mock import MagicMock, AsyncMock, patch

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Photo, Like
from src.services.cloudinary import upload_image_to_cloudinary, generate_transformed_image_url
from src.services.rating_calculation import rating_calculation

class TestService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user_id = 1
        self.photo_id = 1
        self.mock_file = MagicMock(spec=UploadFile)
        self.mock_file.content_type = "image/jpeg"
        self.mock_file.read = AsyncMock(return_value=b"fake_image_data")
        self.mock_photo = Photo(
            id=self.photo_id,
            image="http://example.com/photo.jpg",
            description="Old description",
            user_id=1,
            rating=4,
            created_at=datetime.now() - timedelta(days=1),
            updated_at=datetime.now(),
        )

    async def test_rating_calculation(self):
        # Mock database response for likes
        mock_like_result = MagicMock()
        mock_like_result.scalars().all.return_value = [5, 4, 3]  # Example like values
        # Mock database response for photo
        mock_photo_result = MagicMock()
        mock_photo_result.scalar_one_or_none.return_value = self.mock_photo

        # Chain responses for session.execute
        self.session.execute.side_effect = [mock_like_result, mock_photo_result]

        # Call the function
        result = await rating_calculation(self.photo_id, self.session)

        # Assertions for both queries
        like_query = select(Like.like_value).filter_by(photo_id=self.photo_id)
        photo_query = select(Photo).filter_by(id=self.photo_id)

        # Check if the generated queries match expected SQL strings
        executed_queries = [call[0][0] for call in self.session.execute.await_args_list]
        self.assertTrue(str(like_query) in map(str, executed_queries))
        self.assertTrue(str(photo_query) in map(str, executed_queries))

        # Check the result and updated photo
        self.assertEqual(result, self.mock_photo)
        self.assertEqual(result.rating, round(sum([5, 4, 3]) / 3, 2))  # Rating should be 4.0


    @patch("cloudinary.uploader.upload")
    async def test_upload_image_success(self, mock_cloudinary_upload):
        # Настраиваем успешный ответ от Cloudinary
        mock_cloudinary_upload.return_value = {
            "url": "http://example.com/image.jpg",
            "public_id": "unique_public_id",
        }

        # Вызываем тестируемую функцию
        url, public_id = await upload_image_to_cloudinary(self.mock_file)

        # Проверяем результат
        self.assertEqual(url, "http://example.com/image.jpg")
        self.assertEqual(public_id, "unique_public_id")

        # Проверяем вызов mock_cloudinary_upload
        mock_cloudinary_upload.assert_called_once()

    @patch("cloudinary.uploader.upload")
    async def test_upload_image_invalid_file_type(self, mock_cloudinary_upload):
        # Изменяем тип файла на неподдерживаемый
        self.mock_file.content_type = "application/pdf"

        # Проверяем, что вызывается HTTPException
        with self.assertRaises(HTTPException) as context:
            await upload_image_to_cloudinary(self.mock_file)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid file type. Only JPEG and PNG are allowed.", context.exception.detail)

        # Проверяем, что Cloudinary не вызывается
        mock_cloudinary_upload.assert_not_called()

    @patch("cloudinary.uploader.upload")
    async def test_upload_image_cloudinary_failure(self, mock_cloudinary_upload):
        # Настраиваем Cloudinary для выброса исключения
        mock_cloudinary_upload.side_effect = Exception("Cloudinary error")

        # Проверяем, что вызывается HTTPException
        with self.assertRaises(HTTPException) as context:
            await upload_image_to_cloudinary(self.mock_file)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Error uploading image: Cloudinary error", context.exception.detail)

        # Проверяем вызов mock_cloudinary_upload
        mock_cloudinary_upload.assert_called_once()


    @patch("cloudinary.utils.cloudinary_url")
    def test_generate_transformed_image_url_success(self, mock_cloudinary_url):
        # Настройка mock для успешного ответа
        mock_cloudinary_url.return_value = ("https://example.com/transformed_image.jpg", {})

        public_id = "sample_public_id"
        transformations = {"width": 100, "height": 100, "crop": "fill"}

        # Вызов функции
        result = generate_transformed_image_url(public_id, transformations)

        # Проверка результата
        self.assertEqual(result, "https://example.com/transformed_image.jpg")
        mock_cloudinary_url.assert_called_once_with(public_id, **transformations)


    @patch("cloudinary.utils.cloudinary_url")
    def test_generate_transformed_image_url_failure(self, mock_cloudinary_url):
        # Настройка mock для выброса исключения
        mock_cloudinary_url.side_effect = Exception("Invalid transformations")

        public_id = "sample_public_id"
        transformations = {"width": "invalid", "height": 100, "crop": "fill"}

        # Проверка, что выбрасывается HTTPException
        with self.assertRaises(HTTPException) as context:
            generate_transformed_image_url(public_id, transformations)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Error generating transformed URL: Invalid transformations", context.exception.detail)
        mock_cloudinary_url.assert_called_once_with(public_id, **transformations)


if __name__ == "__main__":
    unittest.main()