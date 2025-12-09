"""
Cloudinary utilities for image upload and management
Works seamlessly with face detection system
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
import base64
import io
from PIL import Image
import os
from django.core.files.base import ContentFile

def configure_cloudinary():
    """Configure Cloudinary with environment variables"""
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )

def upload_base64_to_cloudinary(base64_image, folder="employee_faces", public_id=None):
    """
    Upload base64 image to Cloudinary
    Returns: (cloudinary_url, cloudinary_public_id)
    """
    try:
        # Remove data URL prefix if present
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]
        
        # Decode base64 to bytes
        image_data = base64.b64decode(base64_image)
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            io.BytesIO(image_data),
            folder=folder,
            public_id=public_id,
            resource_type="image",
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        
        return upload_result['secure_url'], upload_result['public_id']
        
    except Exception as e:
        print(f"❌ Cloudinary upload error: {e}")
        raise e

def upload_file_to_cloudinary(file_obj, folder="employee_faces", public_id=None):
    """
    Upload file object to Cloudinary
    Returns: (cloudinary_url, cloudinary_public_id)
    """
    try:
        upload_result = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            public_id=public_id,
            resource_type="image",
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        
        return upload_result['secure_url'], upload_result['public_id']
        
    except Exception as e:
        print(f"❌ Cloudinary upload error: {e}")
        raise e

def get_image_from_cloudinary(public_id):
    """
    Get image URL from Cloudinary public_id
    Returns: cloudinary_url
    """
    try:
        resource = cloudinary.api.resource(public_id)
        return resource['secure_url']
    except Exception as e:
        print(f"❌ Cloudinary get image error: {e}")
        return None

def delete_image_from_cloudinary(public_id):
    """
    Delete image from Cloudinary
    Returns: success (bool)
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"❌ Cloudinary delete error: {e}")
        return False

def optimize_image_for_face_detection(image_url):
    """
    Get optimized image URL for face detection
    Cloudinary automatically optimizes images
    """
    # Cloudinary automatically optimizes images
    # You can add specific transformations if needed
    return image_url

# Face detection compatible functions
def prepare_image_for_face_detection(base64_image):
    """
    Prepare image for face detection (same as current system)
    Returns: PIL Image object
    """
    if "," in base64_image:
        base64_image = base64_image.split(",")[1]
    
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    return image

def cloudinary_to_base64(cloudinary_url):
    """
    Convert Cloudinary URL back to base64 (if needed for face detection)
    Note: This is usually not needed as face detection works with URLs too
    """
    import requests
    
    try:
        response = requests.get(cloudinary_url)
        image_data = response.content
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_data}"
    except Exception as e:
        print(f"❌ Cloudinary to base64 error: {e}")
        return None 