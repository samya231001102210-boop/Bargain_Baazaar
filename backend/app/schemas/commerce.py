from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    listing_id: str
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)

class OrderCreate(BaseModel):
    offer_id: str

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
