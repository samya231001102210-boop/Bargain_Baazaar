from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def profile(user=Depends(get_current_user)):
    return {"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user["role"], "created_at": user.get("created_at")}
