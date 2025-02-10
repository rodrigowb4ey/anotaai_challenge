from datetime import UTC, datetime
from typing import Annotated, Any, ClassVar

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, EmailStr, Field


def parse_object_id(value: str | ObjectId) -> str:
    """Parse ObjectId to string."""
    if isinstance(value, ObjectId):
        return str(value)
    return value


PyObjectId = Annotated[str, BeforeValidator(parse_object_id)]


class User(BaseModel):
    """User model."""

    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    email: EmailStr
    hashed_password: str
    full_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True

    class Config:
        """Pydantic config."""

        populate_by_name = True
        json_schema_extra: ClassVar[dict[str, Any]] = {
            'example': {
                'email': 'john@example.com',
                'full_name': 'John Doe',
                'hashed_password': '<hashed_password>',
                'is_active': True,
            }
        }


class Category(BaseModel):
    """Category model."""

    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    name: str
    description: str | None = None
    owner_id: PyObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        """Pydantic config."""

        populate_by_name = True
        json_schema_extra: ClassVar[dict[str, Any]] = {
            'example': {
                'name': 'Electronics',
                'description': 'Electronic devices and accessories',
                'owner_id': '<owner_id>',
            }
        }


class Product(BaseModel):
    """Product model."""

    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias='_id')
    name: str
    description: str | None = None
    price: float = Field(gt=0)
    category_id: PyObjectId
    owner_id: PyObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        """Pydantic config."""

        populate_by_name = True
        json_schema_extra: ClassVar[dict[str, Any]] = {
            'example': {
                'name': 'Smartphone',
                'description': 'Latest model smartphone',
                'price': 999.99,
                'category_id': '<category_id>',
                'owner_id': '<owner_id>',
            }
        }
