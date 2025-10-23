from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.constants import DB_NAMING_CONVENTION

engine = create_async_engine(
    url=str(settings.get_database_uri()),
    isolation_level=settings.ISOLATION_LEVEL,
    pool_size=settings.DB_ENGINE_POOL_SIZE,
    pool_recycle=settings.DB_ENGINE_POOL_RECYCLE,
    pool_pre_ping=settings.DB_ENGINE_POOL_PRE_PING,
    echo=settings.DB_ENGINE_ECHO,
)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
