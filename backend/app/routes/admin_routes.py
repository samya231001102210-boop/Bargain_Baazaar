from fastapi import APIRouter, Depends
from app.config.database import get_database
from app.utils.dependencies import require_roles

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/summary")
async def summary(user=Depends(require_roles("admin"))):
    db = get_database()
    return {"users": await db.users.count_documents({}), "listings": await db.listings.count_documents({}),
            "offers": await db.offers.count_documents({}), "orders": await db.orders.count_documents({})}
