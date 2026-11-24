from fastapi import APIRouter, Depends
from app.schemas.auth import RegisterInput, LoginInput
from app.services.auth_service import register_user, login_user
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=201)
async def register(data: RegisterInput):
    return await register_user(data)

@router.post("/login")
async def login(data: LoginInput):
    return await login_user(data)

@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user["role"]}
