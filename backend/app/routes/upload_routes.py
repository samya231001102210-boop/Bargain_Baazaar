from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.config.cloudinary import configure_cloudinary
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("/image")
async def upload_image(file: UploadFile = File(...), user=Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image uploads are allowed")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "Image must be 5 MB or smaller")
    if not configure_cloudinary():
        raise HTTPException(503, "Cloudinary credentials are not configured")
    import cloudinary.uploader
    result = cloudinary.uploader.upload(content, folder="bargain_baazaar")
    return {"url": result["secure_url"], "public_id": result["public_id"]}
