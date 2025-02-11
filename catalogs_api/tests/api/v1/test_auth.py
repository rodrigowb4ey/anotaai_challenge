from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorDatabase

pytestmark = pytest.mark.asyncio


async def test_register_user(
    client: TestClient,
    mongodb: AsyncIOMotorDatabase[Any],
) -> None:
    """Test user registration.

    Should successfully register a new user and save it to the database.
    """
    # Arrange
    user_data = {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'full_name': 'Test User',
    }

    # Act
    response = client.post('/api/v1/auth/register', json=user_data)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'id' in data

    # Verify user was saved in database
    user = await mongodb['users'].find_one({'email': user_data['email']})
    assert user is not None
    assert user['full_name'] == user_data['full_name']


async def test_register_duplicate_email(
    client: TestClient,
    mongodb: AsyncIOMotorDatabase[Any],  # noqa: ARG001
) -> None:
    """Test registration with duplicate email.

    Should prevent registration of users with duplicate emails.
    """
    # Arrange
    user_data = {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'full_name': 'Test User',
    }
    duplicate_data = {
        'email': 'test@example.com',  # Same email
        'password': 'different_password',
        'full_name': 'Different User',
    }

    # Act
    # Register first user
    response = client.post('/api/v1/auth/register', json=user_data)
    assert response.status_code == status.HTTP_200_OK

    # Try to register duplicate
    response = client.post('/api/v1/auth/register', json=duplicate_data)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Email already registered' in response.json()['detail']


async def test_login_success(
    client: TestClient,
    mongodb: AsyncIOMotorDatabase[Any],  # noqa: ARG001
) -> None:
    """Test successful login.

    Should allow login with correct credentials and return a valid token.
    """
    # Arrange
    user_data = {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'full_name': 'Test User',
    }
    client.post('/api/v1/auth/register', json=user_data)

    # Act
    response = client.post(
        '/api/v1/auth/login',
        data={
            'username': user_data['email'],
            'password': user_data['password'],
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'  # noqa: S105


async def test_login_wrong_password(
    client: TestClient,
    mongodb: AsyncIOMotorDatabase[Any],  # noqa: ARG001
) -> None:
    """Test login with wrong password.

    Should prevent login with incorrect credentials.
    """
    # Arrange
    user_data = {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'full_name': 'Test User',
    }
    client.post('/api/v1/auth/register', json=user_data)

    # Act
    response = client.post(
        '/api/v1/auth/login',
        data={
            'username': user_data['email'],
            'password': 'wrongpassword',
        },
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'Incorrect email or password' in response.json()['detail']
