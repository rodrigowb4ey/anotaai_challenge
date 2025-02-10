from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.database.mongodb import close_mongo_connection, connect_to_mongo


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Handle startup and shutdown events.

    Yields:
        None
    """
    await connect_to_mongo()

    yield

    await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version='1.0.0',
    description='API for managing product catalogs',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
)


@app.get('/')
async def root() -> dict[str, str]:
    """Root endpoint for health check."""
    return {
        'status': 'ok',
        'message': f'Welcome to {settings.PROJECT_NAME}',
    }
