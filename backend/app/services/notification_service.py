from datetime import datetime, timezone
from app.config.database import get_database

async def create_notification(user_id: str, title: str, message: str, kind: str = "general"):
    await get_database().notifications.insert_one({"user_id": user_id, "title": title,
        "message": message, "kind": kind, "is_read": False, "created_at": datetime.now(timezone.utc)})
