from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from app.config.database import get_database
from app.schemas.listing import ListingCreate, ListingUpdate
from app.utils.dependencies import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/listings", tags=["Listings"])

@router.get("/")
async def browse_listings(category_id: str | None = None, listing_type: str | None = None,
                          search: str | None = None, min_price: float | None = None,
                          max_price: float | None = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    query = {"is_active": True}
    if category_id:
        if not ObjectId.is_valid(category_id): raise HTTPException(400, "Invalid category id")
        query["category_id"] = category_id
    if listing_type:
        if listing_type not in ("product", "service"): raise HTTPException(400, "Invalid listing type")
        query["listing_type"] = listing_type
    if search: query["$text"] = {"$search": search}
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None: query["price"]["$gte"] = min_price
        if max_price is not None: query["price"]["$lte"] = max_price
    db = get_database()
    total = await db.listings.count_documents(query)
    docs = await db.listings.find(query).sort("created_at", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": [serialize(x) for x in docs], "page": page, "limit": limit, "total": total}

@router.post("/", status_code=201)
async def create_listing(data: ListingCreate, user=Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(data.category_id): raise HTTPException(400, "Invalid category id")
    category = await db.categories.find_one({"_id": ObjectId(data.category_id), "is_active": True})
    if not category: raise HTTPException(404, "Category not found")
    if category["kind"] not in ("both", data.listing_type): raise HTTPException(400, "This category does not accept this listing type")
    doc = data.model_dump()
    doc.update({"seller_id": str(user["_id"]), "is_active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)})
    result = await db.listings.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return serialize(doc)

@router.get("/{listing_id}")
async def get_listing(listing_id: str):
    if not ObjectId.is_valid(listing_id): raise HTTPException(400, "Invalid listing id")
    doc = await get_database().listings.find_one({"_id": ObjectId(listing_id), "is_active": True})
    if not doc: raise HTTPException(404, "Listing not found")
    return serialize(doc)

@router.patch("/{listing_id}")
async def update_listing(listing_id: str, data: ListingUpdate, user=Depends(get_current_user)):
    if not ObjectId.is_valid(listing_id): raise HTTPException(400, "Invalid listing id")
    changes = data.model_dump(exclude_unset=True)
    changes["updated_at"] = datetime.now(timezone.utc)
    result = await get_database().listings.update_one({"_id": ObjectId(listing_id), "seller_id": str(user["_id"])}, {"$set": changes})
    if not result.matched_count: raise HTTPException(404, "Listing not found or you are not its owner")
    return {"message": "Listing updated"}

@router.delete("/{listing_id}")
async def delete_listing(listing_id: str, user=Depends(get_current_user)):
    if not ObjectId.is_valid(listing_id): raise HTTPException(400, "Invalid listing id")
    result = await get_database().listings.update_one({"_id": ObjectId(listing_id), "seller_id": str(user["_id"])}, {"$set": {"is_active": False}})
    if not result.matched_count: raise HTTPException(404, "Listing not found or you are not its owner")
    return {"message": "Listing deactivated"}
