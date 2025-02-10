from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """User base schema."""

    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User create schema."""

    password: str


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema."""

    id: str
    is_active: bool

    class Config:
        """Pydantic config."""

        from_attributes = True


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str | None = None


class CategoryBase(BaseModel):
    """Category base schema."""

    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    """Category create schema."""


class CategoryUpdate(BaseModel):
    """Category update schema."""

    name: str | None = None
    description: str | None = None


class CategoryResponse(CategoryBase):
    """Category response schema."""

    id: str
    owner_id: str
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CategoryInDB(CategoryResponse):
    """Category in DB schema."""


class ProductBase(BaseModel):
    """Product base schema."""

    name: str
    description: str | None = None
    price: float = Field(gt=0)
    category_id: str


class ProductCreate(ProductBase):
    """Product create schema."""


class ProductUpdate(BaseModel):
    """Product update schema."""

    name: str | None = None
    description: str | None = None
    price: float | None = Field(gt=0, default=None)
    category_id: str | None = None


class ProductResponse(ProductBase):
    """Product response schema."""

    id: str
    owner_id: str
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProductInDB(ProductResponse):
    """Product in DB schema."""
