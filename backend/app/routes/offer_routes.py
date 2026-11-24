from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.config.database import get_database
from app.schemas.offer import OfferCreate, OfferAction
from app.utils.dependencies import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/offers", tags=["Negotiation"])

@router.post("/", status_code=201)
async def make_offer(data: OfferCreate, user=Depends(get_current_user)):
    db = get_database()
    if not ObjectId.is_valid(data.listing_id): raise HTTPException(400, "Invalid listing id")
    listing = await db.listings.find_one({"_id": ObjectId(data.listing_id), "is_active": True})
    if not listing: raise HTTPException(404, "Listing not found")
    if listing["seller_id"] == str(user["_id"]): raise HTTPException(400, "You cannot make an offer on your own listing")
    if not listing.get("negotiable", True): raise HTTPException(400, "This listing is not negotiable")
    doc = {"listing_id": data.listing_id, "buyer_id": str(user["_id"]), "seller_id": listing["seller_id"],
           "amount": data.amount, "message": data.message, "status": "pending",
           "history": [{"by": str(user["_id"]), "amount": data.amount, "message": data.message, "at": datetime.now(timezone.utc)}],
           "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}
    result = await db.offers.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return serialize(doc)

@router.get("/mine")
async def my_offers(user=Depends(get_current_user)):
    uid = str(user["_id"])
    docs = await get_database().offers.find({"$or": [{"buyer_id": uid}, {"seller_id": uid}]}).sort("updated_at", -1).to_list(200)
    return [serialize(x) for x in docs]

@router.post("/{offer_id}/action")
async def act_on_offer(offer_id: str, data: OfferAction, user=Depends(get_current_user)):
    if not ObjectId.is_valid(offer_id): raise HTTPException(400, "Invalid offer id")
    db = get_database()
    offer = await db.offers.find_one({"_id": ObjectId(offer_id)})
    if not offer: raise HTTPException(404, "Offer not found")
    uid = str(user["_id"])
    if uid not in (offer["buyer_id"], offer["seller_id"]): raise HTTPException(403, "Not part of this negotiation")
    if offer["status"] != "pending": raise HTTPException(400, "This offer is no longer pending")
    is_seller = uid == offer["seller_id"]
    if data.action in ("accept", "reject") and not is_seller:
        raise HTTPException(403, "Only the seller can accept or reject the current offer")
    if data.action == "counter":
        if data.counter_amount is None: raise HTTPException(400, "counter_amount is required")
        if is_seller and offer["history"][-1]["by"] == offer["seller_id"]:
            raise HTTPException(400, "Wait for the buyer to respond to your counteroffer")
        if not is_seller and offer["history"][-1]["by"] == offer["buyer_id"]:
            raise HTTPException(400, "Wait for the seller to respond to your counteroffer")
        event = {"by": uid, "amount": data.counter_amount, "message": data.message, "at": datetime.now(timezone.utc)}
        await db.offers.update_one({"_id": offer["_id"]}, {"$set": {"amount": data.counter_amount, "updated_at": datetime.now(timezone.utc)}, "$push": {"history": event}})
    elif data.action == "accept":
        await db.offers.update_one({"_id": offer["_id"]}, {"$set": {"status": "accepted", "accepted_at": datetime.now(timezone.utc)}})
    else:
        await db.offers.update_one({"_id": offer["_id"]}, {"$set": {"status": "rejected", "updated_at": datetime.now(timezone.utc)}})
    return {"message": f"Offer {data.action}ed" if data.action != "counter" else "Counteroffer sent"}
