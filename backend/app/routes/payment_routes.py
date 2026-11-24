from datetime import datetime, timezone
import hashlib, hmac
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from app.config.database import get_database
from app.config.settings import settings
from app.schemas.commerce import PaymentVerify
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-order/{order_id}")
async def create_payment_order(order_id: str, user=Depends(get_current_user)):
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(503, "Razorpay credentials are not configured")
    if not ObjectId.is_valid(order_id): raise HTTPException(400, "Invalid order id")
    order = await get_database().orders.find_one({"_id": ObjectId(order_id), "buyer_id": str(user["_id"]), "status": "payment_pending"})
    if not order: raise HTTPException(404, "Payable order not found")
    import razorpay
    client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
    rp_order = client.order.create({"amount": int(round(order["amount"] * 100)), "currency": "INR",
                                    "receipt": str(order["_id"])})
    await get_database().orders.update_one({"_id": order["_id"]}, {"$set": {"razorpay_order_id": rp_order["id"]}})
    await get_database().payments.insert_one({"order_id": str(order["_id"]), "razorpay_order_id": rp_order["id"],
        "amount": order["amount"], "currency": "INR", "status": "created", "created_at": datetime.now(timezone.utc)})
    return {"razorpay_order_id": rp_order["id"], "amount": rp_order["amount"], "currency": "INR",
            "key_id": settings.razorpay_key_id}

@router.post("/verify")
async def verify_payment(data: PaymentVerify, user=Depends(get_current_user)):
    if not settings.razorpay_key_secret: raise HTTPException(503, "Razorpay credentials are not configured")
    expected = hmac.new(settings.razorpay_key_secret.encode(), f"{data.razorpay_order_id}|{data.razorpay_payment_id}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, data.razorpay_signature): raise HTTPException(400, "Payment signature verification failed")
    db = get_database()
    order = await db.orders.find_one({"razorpay_order_id": data.razorpay_order_id, "buyer_id": str(user["_id"])})
    if not order: raise HTTPException(404, "Order not found")
    await db.orders.update_one({"_id": order["_id"]}, {"$set": {"status": "paid", "paid_at": datetime.now(timezone.utc)}})
    await db.payments.update_one({"razorpay_order_id": data.razorpay_order_id}, {"$set": {
        "razorpay_payment_id": data.razorpay_payment_id, "status": "paid", "verified_at": datetime.now(timezone.utc)}})
    return {"message": "Payment verified", "order_id": str(order["_id"]), "status": "paid"}

@router.post("/webhook")
async def razorpay_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not settings.razorpay_webhook_secret: raise HTTPException(503, "Webhook secret is not configured")
    expected = hmac.new(settings.razorpay_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature): raise HTTPException(400, "Invalid webhook signature")
    payload = await request.json()
    if payload.get("event") == "payment.captured":
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        if entity.get("order_id"):
            await get_database().orders.update_one({"razorpay_order_id": entity["order_id"]},
                {"$set": {"status": "paid", "paid_at": datetime.now(timezone.utc)}})
    return {"received": True}
