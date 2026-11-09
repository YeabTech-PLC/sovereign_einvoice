from collections.abc import AsyncIterator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.sql_echo,
    pool_pre_ping=True,
    pool_size=settings.postgres_pool_size,
    max_overflow=settings.postgres_max_overflow,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide a database session and always close it."""
    async with AsyncSessionLocal() as session:
        yield session


async def set_tenant_context(
    session: AsyncSession,
    tenant_id: UUID,
) -> None:
    """
    Set transaction-local PostgreSQL tenant context.

    Call only after authentication and authorization have established
    that the user is allowed to access this tenant.

    This must happen before querying tenant-scoped records and within
    the same database transaction as those queries.
    """
    await session.execute(
        text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )
