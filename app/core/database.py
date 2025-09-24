from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings
from typing import AsyncGenerator

settings = get_settings()

# Motor asíncrono PostgreSQL con opciones de pool
async_engine = create_async_engine(
    settings.database_url_async,
    echo=settings.app_env == "development",
    future=True,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_timeout=settings.pool_timeout,
    pool_recycle=settings.pool_recycle,
)

# Factory de sesiones asincrónicas
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()

async def close_async_engine():
    await async_engine.dispose()
