from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.database.mongodb import get_database
from app.models import Product, User
from app.schemas import ProductCreate, ProductUpdate

router = APIRouter()


@router.post('/')
async def create_product(
    product_in: ProductCreate,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Product:
    """Create new product."""
    category = await db.categories.find_one({'_id': product_in.category_id, 'owner_id': str(current_user.id)})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found',
        )

    product = Product(
        **product_in.model_dump(),
        owner_id=str(current_user.id),
    )

    result = await db.products.insert_one(product.model_dump(by_alias=True))
    product.id = str(result.inserted_id)
    return product


@router.get('/')
async def list_products(
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Product]:
    """List all products for current user."""
    cursor = db.products.find({'owner_id': str(current_user.id)})
    products = await cursor.to_list(length=None)
    return [Product(**product) for product in products]


@router.get('/{product_id}')
async def get_product(
    product_id: str,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Product:
    """Get a specific product."""
    product = await db.products.find_one({'_id': product_id, 'owner_id': str(current_user.id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found',
        )
    return Product(**product)


@router.put('/{product_id}')
async def update_product(
    product_id: str,
    product_in: ProductUpdate,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Product:
    """Update a product."""
    product = await db.products.find_one({'_id': product_id, 'owner_id': str(current_user.id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found',
        )

    update_data = product_in.model_dump(exclude_unset=True)

    if 'category_id' in update_data:
        category = await db.categories.find_one({'_id': update_data['category_id'], 'owner_id': str(current_user.id)})
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Category not found',
            )

    if update_data:
        await db.products.update_one({'_id': product_id}, {'$set': update_data})

    updated_product = await db.products.find_one({'_id': product_id})
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found',
        )
    return Product(**updated_product)


@router.delete('/{product_id}')
async def delete_product(
    product_id: str,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a product."""
    result = await db.products.delete_one({'_id': product_id, 'owner_id': str(current_user.id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found',
        )
    return {'message': 'Product deleted successfully'}
