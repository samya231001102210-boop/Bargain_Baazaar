import re
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.config.database import get_database
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.dependencies import require_roles
from app.utils.serializers import serialize

router = APIRouter(prefix="/categories", tags=["Categories"])

def slugify(value):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")

@router.get("/")
async def list_categories():
    docs = await get_database().categories.find({"is_active": True}).sort("name", 1).to_list(200)
    return [serialize(x) for x in docs]

@router.post("/", status_code=201)
async def create_category(data: CategoryCreate, user=Depends(require_roles("admin"))):
    doc = data.model_dump()
    doc.update({"slug": slugify(data.name), "is_active": True, "created_at": datetime.now(timezone.utc)})
    try:
        result = await get_database().categories.insert_one(doc)
    except Exception:
        raise HTTPException(status_code=409, detail="A category with this name/slug may already exist")
    doc["id"] = str(result.inserted_id)
    return serialize(doc)

@router.patch("/{category_id}")
async def update_category(category_id: str, data: CategoryUpdate, user=Depends(require_roles("admin"))):
    from bson import ObjectId
    if not ObjectId.is_valid(category_id):
        raise HTTPException(status_code=400, detail="Invalid category id")
    changes = {k:v for k,v in data.model_dump(exclude_unset=True).items()}
    if "name" in changes:
        changes["slug"] = slugify(changes["name"])
    result = await get_database().categories.update_one({"_id": ObjectId(category_id)}, {"$set": changes})
    if not result.matched_count:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category updated"}
