import secrets
from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    ISOLATION_LEVEL: str = 'REPEATABLE READ'

    UVICORN_HOST: str = '0.0.0.0'
    UVICORN_PORT: int = 8000
    UVICORN_WORKERS: int = 1

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DB_ENGINE_ECHO: bool | Literal['debug'] = False
    DB_ENGINE_POOL_SIZE: int = 20
    DB_ENGINE_POOL_RECYCLE: int = 60 * 60  # 1 hour
    DB_ENGINE_POOL_PRE_PING: bool = True

    JWT_SECRET: str = secrets.token_urlsafe(32)

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
