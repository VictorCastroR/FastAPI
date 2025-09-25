from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from app.core.config import get_settings

settings = get_settings()

def custom_key_func(request: Request) -> str:
    """
    Determina la clave de rate limiting.
    Si el usuario está autenticado y tiene id, usa ese.
    Si no, usa la IP del cliente.
    """
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return str(user.id)
    return get_remote_address(request)

limiter = Limiter(
    key_func=custom_key_func,
    default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_minutes}minute"]
)

__all__ = ["limiter"]
