from fastapi import APIRouter, Depends
from app.config.database import get_database
from app.utils.dependencies import get_current_user
from app.utils.serializers import serialize

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
async def notifications(user=Depends(get_current_user)):
    docs = await get_database().notifications.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(100)
    return [serialize(x) for x in docs]
