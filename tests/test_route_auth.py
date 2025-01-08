from unittest.mock import Mock
import pytest
from sqlalchemy import select

from tests.conftest import TestingSessionLocal
from src.entity.models import User

user_data = {"username": "test1", "email": "test1@example.com", "hash": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user_data,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == user_data.get("email")
    assert "hash" not in data
    assert "avatar" in data
    assert "id" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user_data,
    )

    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_not_confirmed_login(client):
    response = client.post("/api/auth/login",
                           data={"username": "email",
                                 "password": user_data.get("hash")}
                           )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("/api/auth/login",
                           data={"username": user_data.get("email"),
                                 "password": user_data.get("hash")}
                           )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    response = client.post(
        "/api/auth/login",
        data={"username": user_data.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user_data.get('hash')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"
