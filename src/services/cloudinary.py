import cloudinary
import hashlib
import time
from cloudinary.utils import cloudinary_url
import hmac
import os
from fastapi import HTTPException, UploadFile
from src.conf.config import config
import logging
import cloudinary.uploader
import cloudinary.api


logger = logging.getLogger(__name__)

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
)
async def upload_image_to_cloudinary(file: UploadFile) -> tuple[str, str]:
    """
    Uploads the given image file to Cloudinary and returns the uploaded image URL and public ID.

    Args:
        file: The image file to upload.

    Returns:
        A tuple containing the uploaded image URL and public ID.

    Raises:
        HTTPException: If the file type is invalid or there is an error with the upload.
    """
    try:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")

        timestamp = int(time.time())


        params_to_sign = f"timestamp={timestamp}"
        signature = hmac.new(
            bytes(config.CLD_API_SECRET, 'utf-8'),
            msg=bytes(params_to_sign, 'utf-8'),
            digestmod=hashlib.sha1
        ).hexdigest()


        file_content = await file.read()

        response = cloudinary.uploader.upload(
            file_content,
            resource_type="image",
            api_key=config.CLD_API_KEY,
            timestamp=timestamp,
            signature=signature
        )


        return response.get("url"), response.get("public_id")

    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error uploading image: {str(e)}")


def generate_transformed_image_url(public_id: str, transformations: dict):
    """
    Generates a Cloudinary URL with the given transformations.

    Args:
        public_id (str): The public ID of the image.
        transformations (dict): A dictionary of transformations to apply.

    Returns:
        str: A Cloudinary URL with the given transformations.
    """
    try:

        url = cloudinary.utils.cloudinary_url(public_id, **transformations)[0]
        logger.debug(f"Generated transformed URL: {url}")
        return url
    except Exception as e:
        logger.error(f"Error generating transformed URL: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error generating transformed URL: {str(e)}")