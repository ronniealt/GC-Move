import logging
import logging.config
import time
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routers import advisor, dashboard, evaluations, families, inspections, invite, journal, preferences, properties, schools, suburbs

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s — %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "root": {"handlers": ["console"], "level": settings.LOG_LEVEL},
})

logger = logging.getLogger(__name__)

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm the connection pool so the first real request doesn't pay
    # the cold TCP + TLS + auth cost to the remote DB.
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection pool warmed up")
    except Exception as e:
        logger.warning("Could not pre-warm DB pool: %s", e)
    yield
    await engine.dispose()


app = FastAPI(title="GC Move OS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_header(request: Request, call_next) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.0f}"
    logger.info("%-6s %-40s → %d  %.0fms", request.method, request.url.path, response.status_code, elapsed_ms)
    return response

app.include_router(families.router)
app.include_router(invite.router)
app.include_router(dashboard.router)
app.include_router(properties.router)
app.include_router(evaluations.router, prefix="/api")
app.include_router(advisor.router)
app.include_router(suburbs.router)
app.include_router(schools.router)
app.include_router(preferences.router)
app.include_router(journal.router)
app.include_router(inspections.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
