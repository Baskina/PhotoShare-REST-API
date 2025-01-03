from io import BytesIO
import qrcode
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


async def upload_image_to_cloudinary(file: UploadFile):
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
    try:

        url = cloudinary.utils.cloudinary_url(public_id, **transformations)[0]
        logger.debug(f"Generated transformed URL: {url}")
        return url
    except Exception as e:
        logger.error(f"Error generating transformed URL: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error generating transformed URL: {str(e)}")


async def upload_qr_to_cloudinary(link_url):
    try:
        timestamp = int(time.time())

        params_to_sign = f"timestamp={timestamp}"
        signature = hmac.new(
            bytes(config.CLD_API_SECRET, 'utf-8'),
            msg=bytes(params_to_sign, 'utf-8'),
            digestmod=hashlib.sha1
        ).hexdigest()

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(link_url)
        qr.make(fit=True)
        # Convert QR code to a byte stream
        img = qr.make_image(fill="black", back_color="white")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr)
        img_byte_arr.seek(0)

        upload_result = cloudinary.uploader.upload(
            img_byte_arr,
            folder="qr_codes",
            api_key=config.CLD_API_KEY,
            timestamp=timestamp,
            signature=signature
        )

        return upload_result.get("url")

    except Exception as e:
        logger.error(f"Error uploading QR code: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error uploading image: {str(e)}")
