from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.mongodb import get_database
from app.models import User
from app.schemas import Token, UserCreate, UserResponse

router = APIRouter()


@router.post('/login')
async def login(
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Login user."""
    user_dict = await db.users.find_one({'email': form_data.username})
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = User(**user_dict)
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type='bearer')  # noqa: S106


@router.post('/register')
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncIOMotorDatabase[Any], Depends(get_database)],
) -> UserResponse:
    """Register new user."""
    existing_user = await db.users.find_one({'email': user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered',
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )

    result = await db.users.insert_one(user.model_dump(by_alias=True))
    user.id = str(result.inserted_id)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )
