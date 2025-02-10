from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.database.mongodb import get_database
from app.models import Category, User
from app.schemas import CategoryCreate, CategoryUpdate

router = APIRouter()


@router.post('/')
async def create_category(
    category_in: CategoryCreate,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Category:
    """Create new category."""
    category = Category(
        **category_in.model_dump(),
        owner_id=str(current_user.id),
    )

    result = await db.categories.insert_one(category.model_dump(by_alias=True))
    category.id = str(result.inserted_id)
    return category


@router.get('/')
async def list_categories(
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Category]:
    """List all categories for current user."""
    cursor = db.categories.find({'owner_id': str(current_user.id)})
    categories = await cursor.to_list(length=None)
    return [Category(**category) for category in categories]


@router.get('/{category_id}')
async def get_category(
    category_id: str,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Category:
    """Get a specific category."""
    category = await db.categories.find_one({'_id': category_id, 'owner_id': str(current_user.id)})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found',
        )
    return Category(**category)


@router.put('/{category_id}')
async def update_category(
    category_id: str,
    category_in: CategoryUpdate,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Category:
    """Update a category."""
    category = await db.categories.find_one({'_id': category_id, 'owner_id': str(current_user.id)})
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found',
        )

    update_data = category_in.model_dump(exclude_unset=True)
    if update_data:
        await db.categories.update_one({'_id': category_id}, {'$set': update_data})

    updated_category = await db.categories.find_one({'_id': category_id})
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found after update',
        )
    return Category(**updated_category)


@router.delete('/{category_id}')
async def delete_category(
    category_id: str,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a category."""
    product = await db.products.find_one({'category_id': category_id})
    if product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot delete category with associated products',
        )

    result = await db.categories.delete_one({'_id': category_id, 'owner_id': str(current_user.id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found',
        )
    return {'message': 'Category deleted successfully'}
