from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi
from app.config.settings import settings

client: AsyncMongoClient | None = None
db = None

async def connect_to_mongodb():
    global client, db
    client = AsyncMongoClient(settings.mongodb_uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=10000)
    await client.admin.command("ping")
    db = client[settings.mongodb_database]
    await db.users.create_index("email", unique=True)
    await db.categories.create_index("slug", unique=True)
    await db.listings.create_index([("title", "text"), ("description", "text")])
    await db.offers.create_index([("listing_id", 1), ("buyer_id", 1)])
    print(f"MongoDB connected: {settings.mongodb_database}")

async def close_mongodb_connection():
    global client
    if client:
        await client.close()

def get_database():
    if db is None:
        raise RuntimeError("Database is not connected")
    return db
