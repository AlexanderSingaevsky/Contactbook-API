import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.database_postgres import get_session
from src.models import Base
from main import app

URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(URL, echo=True)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="module")
async def db():
    async with async_session() as session:
        yield session


@pytest.fixture(scope="module")
def client(db):
    async def override_get_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool", "email": "deadpool@example.com", "password": "12345678"}
