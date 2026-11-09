from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import CorrelationIdMiddleware
from app.db.session import engine

settings = get_settings()
logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown resources."""
    configure_logging(settings)

    logger.info(
        "application_starting",
        extra={
            "event": "application_starting",
            "app_env": settings.app_env,
        },
    )

    yield

    await engine.dispose()

    logger.info(
        "application_stopped",
        extra={"event": "application_stopped"},
    )


app = FastAPI(
    title=settings.app_name,
    description="YeabTech multi-tenant electronic invoicing platform API",
    version="0.1.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
    openapi_url="/openapi.json" if settings.app_env == "development" else None,
    lifespan=lifespan,
)

register_exception_handlers(app)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "running",
    }
