import logging
import logging.config

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)

app = FastAPI(title="GC Move OS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
