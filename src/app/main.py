from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.slices.note.router import router as notes_router
from app.slices.tag.router import router as tag_router

router = APIRouter()
router.include_router(notes_router, prefix='/notes', tags=['notes'])
router.include_router(tag_router, prefix='/tags', tags=['tags'])

app = FastAPI(
    title='Notes API',
    summary='Manage notes and tags.',
)
app.include_router(router, prefix=settings.API_V1_STR)


@app.get('/healthcheck', include_in_schema=False)
def healthcheck():
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app='main:app',
        host=settings.UVICORN_HOST,
        port=settings.UVICORN_PORT,
        workers=settings.UVICORN_WORKERS,
    )
