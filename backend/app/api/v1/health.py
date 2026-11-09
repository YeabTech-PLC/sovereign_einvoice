import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
async def liveness() -> dict[str, str]:
    """Confirm that the API process is running."""
    return {"status": "alive"}


@router.get("/ready")
async def readiness() -> dict[str, str]:
    """Check that PostgreSQL accepts an authenticated query."""
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    except SQLAlchemyError as exc:
        # Log only the exception class, not the database error message.
        logger.error(
            "database_readiness_failed",
            extra={
                "event": "database_readiness_failed",
                "exception_type": type(exc).__name__,
            },
        )

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
        ) from None

    return {
        "status": "ready",
        "database": "ok",
    }
