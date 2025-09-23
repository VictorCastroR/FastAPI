from loguru import logger
import sys
from pathlib import Path

# Archivo donde se almacenarán SOLO los logs de errores
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
ERROR_LOG_FILE = LOG_DIR / "errors.log"

# Formato personalizado con contexto para cada error
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
    "<level>{level}</level> - "
    "<cyan>{name}:{function}:{line}</cyan> - "
    "→ {message} | "
    "Extra: {extra}"
)

# Limpia cualquier handler estándar previo
logger.remove()

# Agrega sink asíncrono, guarda solo errores de nivel ERROR o superior
logger.add(
    str(ERROR_LOG_FILE),
    level="ERROR",
    format=LOG_FORMAT,
    enqueue=True,         # Asíncrono y robusto para producción
    rotation="10 MB",     # Rotación por tamaño, ajusta según tu contexto
    retention="10 days",  # Retiene archivos por 10 días
    compression="zip",    # Comprime logs antiguos para ahorro de espacio
    backtrace=True,       # Incluye traceback detallado
    diagnose=True         # Intenta incluir contexto extra y variables
)

# Opcional: también puedes mandar errores críticos a stderr para depuración local (remueve en producción si no lo necesitas)
logger.add(sys.stderr, level="ERROR", format=LOG_FORMAT)

# Exporta el logger para uso global
__all__ = ["logger"]
