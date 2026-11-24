from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.config.database import get_database
from app.utils.dependencies import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.get("/")
async def get_wishlist(user=Depends(get_current_user)):
    docs = await get_database().wishlists.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(300)
    return [serialize(x) for x in docs]

@router.post("/{listing_id}")
async def add_wishlist(listing_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(listing_id): raise HTTPException(400, "Invalid listing id")
    db = get_database()
    if not await db.listings.find_one({"_id": ObjectId(listing_id), "is_active": True}): raise HTTPException(404, "Listing not found")
    uid = str(user["_id"])
    await db.wishlists.update_one({"user_id": uid, "listing_id": listing_id},
        {"$setOnInsert": {"user_id": uid, "listing_id": listing_id, "created_at": datetime.now(timezone.utc)}}, upsert=True)
    return {"message": "Added to wishlist"}

@router.delete("/{listing_id}")
async def remove_wishlist(listing_id: str, user=Depends(get_current_user)):
    await get_database().wishlists.delete_one({"user_id": str(user["_id"]), "listing_id": listing_id})
    return {"message": "Removed from wishlist"}
