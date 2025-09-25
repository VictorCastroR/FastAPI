# main.py
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import close_async_engine
from app.modules.user.router import router as user_router

# ----------------------
# Configuración de settings
# ----------------------
settings = get_settings()

# ----------------------
# Logger
# ----------------------
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(settings.app_name)

# ======================
# Lifespan (startup/shutdown) moderno
# ======================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ----------------------
    # Startup: se ejecuta al iniciar la app
    # ----------------------
    logger.info(f"{settings.app_name} iniciado en modo {settings.app_env}")
    
    # Aquí puedes inicializar otras cosas, ej: cache, colas, servicios externos
    # await init_cache()
    # await init_external_services()

    yield  # La app queda lista para recibir requests

    # ----------------------
    # Shutdown: se ejecuta al cerrar la app
    # ----------------------
    await close_async_engine()  # Cerramos motor de BD
    logger.info(f"{settings.app_name} finalizado y motor de BD cerrado")

# ======================
# Inicialización de FastAPI
# ======================
app = FastAPI(
    title=settings.app_name,
    description=f"{settings.app_name} API",
    version=settings.app_version,
    docs_url=f"{settings.api_prefix}/docs",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan
)

# ======================
# Configuración CORS
# ======================
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Agrega aquí otros dominios permitidos
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# Routers
# ======================
app.include_router(
    user_router,
    prefix=f"{settings.api_prefix}/users",
    tags=["Usuarios"]
)

# ======================
# Ejecución directa (uvicorn)
# ======================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,  # Recarga automática en dev
        log_level=settings.log_level.lower()
    )
