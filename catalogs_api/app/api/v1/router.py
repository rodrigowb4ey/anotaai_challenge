from fastapi import APIRouter

from app.api.v1.endpoints import auth, categories, products

api_router = APIRouter()

api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(products.router, prefix='/products', tags=['products'])
api_router.include_router(categories.router, prefix='/categories', tags=['categories'])
