from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


class MongoDB:
    """MongoDB client."""

    client: AsyncIOMotorClient[Any] | None = None


db = MongoDB()


async def get_database() -> AsyncIOMotorDatabase[Any]:
    """Get the database."""
    if db.client is None:
        raise RuntimeError('Database client is not initialized')
    return db.client[settings.DATABASE_NAME]


async def connect_to_mongo() -> None:
    """Connect to MongoDB."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)


async def close_mongo_connection() -> None:
    """Close the MongoDB connection."""
    if db.client is not None:
        db.client.close()
