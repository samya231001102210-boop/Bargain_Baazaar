from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.config.database import get_database
from app.schemas.commerce import ReviewCreate
from app.utils.dependencies import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", status_code=201)
async def create_review(data: ReviewCreate, user=Depends(get_current_user)):
    if not ObjectId.is_valid(data.listing_id): raise HTTPException(400, "Invalid listing id")
    db = get_database()
    if not await db.listings.find_one({"_id": ObjectId(data.listing_id)}): raise HTTPException(404, "Listing not found")
    doc = {"listing_id": data.listing_id, "user_id": str(user["_id"]), "rating": data.rating,
           "comment": data.comment, "created_at": datetime.now(timezone.utc)}
    result = await db.reviews.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return serialize(doc)

@router.get("/{listing_id}")
async def listing_reviews(listing_id: str):
    docs = await get_database().reviews.find({"listing_id": listing_id}).sort("created_at", -1).to_list(200)
    return [serialize(x) for x in docs]
