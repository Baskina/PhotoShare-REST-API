import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from fastapi_limiter import FastAPILimiter
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import logging

from main import app
from src.entity.models import Base, User
from src.database.db import get_db
from src.services.auth import auth_service

logging.getLogger().setLevel(logging.CRITICAL)

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

test_user = {"username": "deadpool", "email": "deadpool@example.com", "hash": "12345678"}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["hash"])
            current_user = User(username=test_user["username"],
                                email=test_user["email"],
                                hash=hash_password,
                                confirmed=True,
                                role="user")
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as error:
            print(error)
            await session.rollback()
            raise
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module", autouse=True)
async def init_limiter():
    # mock_redis = redis.from_url("redis://localhost:6379", decode_responses=True)
    mock_redis = MagicMock()
    await FastAPILimiter.init(mock_redis)

    yield


@pytest.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token
