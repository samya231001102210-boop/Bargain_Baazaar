import asyncio
from datetime import datetime, timezone
from app.config.database import connect_to_mongodb, close_mongodb_connection, get_database

CATEGORIES = [
    ("Electronics", "Phones, laptops, accessories and gadgets", "product"),
    ("Fashion", "Clothing, shoes, bags and accessories", "product"),
    ("Home & Furniture", "Furniture, appliances and home decor", "product"),
    ("Beauty & Personal Care", "Skincare, cosmetics and grooming", "product"),
    ("Books & Education", "Books, stationery and learning resources", "both"),
    ("Sports & Fitness", "Sportswear and fitness equipment", "product"),
    ("Grocery", "Food and household essentials", "product"),
    ("Services", "Repairs, tutoring, design and professional services", "service"),
    ("Others", "Other products and services", "both"),
]

async def seed():
    await connect_to_mongodb()
    db = get_database()
    for name, description, kind in CATEGORIES:
        slug = name.lower().replace("&", "and").replace(" ", "-")
        await db.categories.update_one({"slug": slug},
            {"$setOnInsert": {"name": name, "description": description, "kind": kind,
                              "is_active": True, "created_at": datetime.now(timezone.utc)}}, upsert=True)
    print("Category seeding complete")
    await close_mongodb_connection()

if __name__ == "__main__":
    asyncio.run(seed())
