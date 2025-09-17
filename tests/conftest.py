import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.db import get_session
from app.core.models import BaseSQLModel
from app.main import app


@pytest_asyncio.fixture(name='session')
async def session_fixture():
    engine = create_async_engine(
        url='sqlite+aiosqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        echo=settings.DB_ENGINE_ECHO,
    )
    async with engine.begin() as conn:
        await conn.run_sync(BaseSQLModel.metadata.create_all)

    try:
        sm = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with sm() as session:
            yield session
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(BaseSQLModel.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture(name='client')
async def client_fixture(session: AsyncSession):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            yield client
    finally:
        app.dependency_overrides.clear()
