from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.config.database import get_database
from app.schemas.commerce import OrderCreate
from app.utils.dependencies import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", status_code=201)
async def create_order(data: OrderCreate, user=Depends(get_current_user)):
    if not ObjectId.is_valid(data.offer_id): raise HTTPException(400, "Invalid offer id")
    db = get_database()
    offer = await db.offers.find_one({"_id": ObjectId(data.offer_id), "status": "accepted", "buyer_id": str(user["_id"])})
    if not offer: raise HTTPException(404, "Accepted offer not found for this buyer")
    existing = await db.orders.find_one({"offer_id": data.offer_id})
    if existing: raise HTTPException(409, "An order already exists for this offer")
    order = {"offer_id": data.offer_id, "listing_id": offer["listing_id"], "buyer_id": offer["buyer_id"],
             "seller_id": offer["seller_id"], "amount": offer["amount"], "currency": "INR",
             "status": "payment_pending", "created_at": datetime.now(timezone.utc)}
    result = await db.orders.insert_one(order)
    order["id"] = str(result.inserted_id)
    return serialize(order)

@router.get("/mine")
async def my_orders(user=Depends(get_current_user)):
    uid = str(user["_id"])
    docs = await get_database().orders.find({"$or": [{"buyer_id": uid}, {"seller_id": uid}]}).sort("created_at", -1).to_list(200)
    return [serialize(x) for x in docs]
