from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import get_settings
from typing import AsyncGenerator

settings = get_settings()

# Motor asíncrono PostgreSQL
async_engine = create_async_engine(
    settings.database_url_async,
    echo=settings.app_env == "development",  # Activa echo solo si es desarrollo
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    future=True
)

# Factory de sesiones asincrónicas
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base declarativa para modelos
Base = declarative_base()

# Dependency para FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para endpoints asincrónicos.
    Crea y cierra automáticamente la sesión en el contexto async.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            raise exc
        finally:
            await session.close()

# Opción para cerrar el motor (usado en shutdown, tests, scripts)
async def close_async_engine():
    await async_engine.dispose()
