from collections.abc import AsyncGenerator
from typing import Any, cast

import pytest
from app.core.config import settings
from app.database.mongodb import db, get_database
from app.main import app
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


@pytest.fixture
async def mongodb() -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    """Create a test database using mongomock."""
    test_db_name = f'{settings.DATABASE_NAME}_test'

    # Create mock client and assign it to db.client
    mock_client = AsyncMongoMockClient()
    db.client = cast(AsyncIOMotorClient[Any], mock_client)

    if db.client is None:
        raise RuntimeError('Database client is not initialized')

    database = db.client[test_db_name]

    # Create users collection explicitly
    await database.create_collection('users')

    # Override the get_database dependency
    async def override_get_database() -> AsyncIOMotorDatabase[Any]:
        return database

    app.dependency_overrides[get_database] = override_get_database

    yield database

    # Clean up
    await database.client.drop_database(test_db_name)
    app.dependency_overrides.clear()


@pytest.fixture
def client(mongodb: AsyncIOMotorDatabase[Any]) -> TestClient:  # noqa: ARG001
    """Create a test client for the FastAPI app."""
    return TestClient(app)
