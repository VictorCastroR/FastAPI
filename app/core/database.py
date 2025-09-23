from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import get_settings

# Obtener configuración
settings = get_settings()

# -------------------------------
# Motor asíncrono (PostgreSQL)
# -------------------------------
async_engine = create_async_engine(
    settings.database_url_async,
    echo=False,  # True en desarrollo para debug
    pool_size=20,         # Tamaño máximo del pool
    max_overflow=10,      # Conexiones extra cuando el pool se llena
    pool_timeout=30,      # Timeout para obtener conexión
    pool_recycle=1800,    # Tiempo para reciclar conexiones
    future=True
)

# -------------------------------
# Factory de sesiones asincrónicas
# -------------------------------
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# -------------------------------
# Base declarativa para modelos
# -------------------------------
Base = declarative_base()

# -------------------------------
# Dependency para FastAPI
# -------------------------------
async def get_async_db():
    """Dependency para endpoints asincrónicos"""
    async with AsyncSessionLocal() as session:
        yield session
