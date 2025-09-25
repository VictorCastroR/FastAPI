from loguru import logger
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
ERROR_LOG_FILE = LOG_DIR / "errors.log"

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
    "<level>{level}</level> - "
    "<cyan>{name}:{function}:{line}</cyan> - "
    "→ {message} | "
    "Extra: {extra}"
)

logger.remove()

# Agrega sink para errores en archivo
logger.add(
    str(ERROR_LOG_FILE),
    level="ERROR",
    format=LOG_FORMAT,
    enqueue=True,
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    backtrace=True,
    diagnose=True
)

# Opcional: salida estándar para errors, útil en desarrollo
logger.add(sys.stderr, level="ERROR", format=LOG_FORMAT)

__all__ = ["logger"]

"""
Ejemplo de uso en la app:

from core.logger import logger

logger.error(
    "Mensaje de error con contexto",
    extra={
        "path": request.url.path,
        "user": getattr(request.state, 'user', None)
    }
)
"""
