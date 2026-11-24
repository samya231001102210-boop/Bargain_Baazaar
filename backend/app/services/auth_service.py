from datetime import datetime, timezone
from fastapi import HTTPException
from app.config.database import get_database
from app.utils.security import hash_password, verify_password, create_access_token

async def register_user(data):
    db = get_database()
    email = data.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    doc = {"name": data.name.strip(), "email": email, "password_hash": hash_password(data.password),
           "role": data.role, "is_active": True, "created_at": datetime.now(timezone.utc)}
    result = await db.users.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    doc.pop("password_hash", None)
    return {"access_token": create_access_token(doc["id"], doc["role"]), "token_type": "bearer", "user": doc}

async def login_user(data):
    db = get_database()
    user = await db.users.find_one({"email": data.email.lower()})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is disabled")
    return {"access_token": create_access_token(str(user["_id"]), user["role"]), "token_type": "bearer",
            "user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user["role"]}}
