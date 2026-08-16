import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import get_ingest_use_case, get_settings
from api.routes import chat, health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — running CV ingestion")
    ingest_use_case = get_ingest_use_case()
    result = ingest_use_case.ingest_all()
    logger.info(
        "Ingestion complete: %d ingested, %d skipped, %d chunks added",
        len(result.ingested_files),
        len(result.skipped_files),
        result.total_chunks,
    )
    yield


def create_app() -> FastAPI:
    app_settings = get_settings()
    app = FastAPI(
        title="AI CV Scanner API",
        description="RAG backend for querying synthetic CV PDFs",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)
    return app


app = create_app()
