from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.middlewares.metrics import MetricsMiddleware, metrics_route
from app.slices.note.constants import SENTENCE_TRANSFORMERS_MODEL
from app.slices.note.router import router as notes_router
from app.slices.tag.router import router as tag_router

router = APIRouter()
router.include_router(notes_router, prefix='/notes', tags=['notes'])
router.include_router(tag_router, prefix='/tags', tags=['tags'])


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield {
        'st': SentenceTransformer(SENTENCE_TRANSFORMERS_MODEL),
    }


app = FastAPI(
    title=settings.APP_NAME,
    summary='Manage notes and tags.',
    version='1.0.0',
    lifespan=lifespan,
)

app.add_middleware(MetricsMiddleware)
app.add_route('/metrics', metrics_route, include_in_schema=False)

app.include_router(router, prefix=settings.API_V1_STR)


@app.get('/healthcheck', include_in_schema=False)
def healthcheck():
    return {'status': 'ok'}
