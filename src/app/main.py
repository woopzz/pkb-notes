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
    version='1.0.0',
)
app.include_router(router, prefix=settings.API_V1_STR)


@app.get('/healthcheck', include_in_schema=False)
def healthcheck():
    return {'status': 'ok'}
