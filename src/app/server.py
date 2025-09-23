import uvicorn

from app.core.config import settings

if __name__ == '__main__':
    uvicorn.run(
        app='app.main:app',
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        workers=settings.UVICORN_WORKERS,
    )
