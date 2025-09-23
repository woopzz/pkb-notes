import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.db import get_session
from app.core.models import BaseSQLModel
from app.core.security import get_current_user_id
from app.main import app
from app.slices.note.models import Note
from app.slices.tag.models import Tag


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


@pytest_asyncio.fixture(name='current_user_id', autouse=True)
async def current_user_id_fixture():
    current_user_id = uuid.uuid4()

    def get_current_user_id_override():
        return current_user_id

    app.dependency_overrides[get_current_user_id] = get_current_user_id_override

    try:
        yield current_user_id
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture()
def create_note(session: AsyncSession, current_user_id: uuid.UUID):
    async def create(**values):
        values.setdefault('name', 'test')
        values.setdefault('content', '')
        values.setdefault('owner_id', current_user_id)
        note = Note(**values)

        session.add(note)
        await session.commit()
        return note

    yield create


@pytest_asyncio.fixture()
def create_tag(session: AsyncSession, current_user_id: uuid.UUID):
    async def create(**values):
        values.setdefault('name', 'test')
        values.setdefault('owner_id', current_user_id)
        tag = Tag(**values)

        session.add(tag)
        await session.commit()
        return tag

    yield create
