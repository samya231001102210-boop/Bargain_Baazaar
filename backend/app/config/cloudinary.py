import cloudinary
from app.config.settings import settings

def configure_cloudinary():
    if settings.cloudinary_cloud_name and settings.cloudinary_api_key and settings.cloudinary_api_secret:
        cloudinary.config(cloud_name=settings.cloudinary_cloud_name,
                          api_key=settings.cloudinary_api_key,
                          api_secret=settings.cloudinary_api_secret,
                          secure=True)
        return True
    return False
