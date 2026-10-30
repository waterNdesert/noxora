from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import get_db_session
from src.main import app
from src.models import Base


@pytest_asyncio.fixture
async def test_session_factory():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await test_engine.dispose()


@pytest_asyncio.fixture
async def client(test_session_factory) -> AsyncIterator[AsyncClient]:
    async def override_session() -> AsyncIterator[AsyncSession]:
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8080",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
