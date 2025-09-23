# Importa el limitador de SlowAPI y la utilidad para obtener la IP remota
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

# Función personalizada para determinar la clave de rate limiting:
# Si el usuario está autenticado (guardado en request.state.user y tiene atributo id), usa su id.
# Si no hay usuario autenticado, usa la IP remota del cliente.
def custom_key_func(request: Request) -> str:
    user = getattr(request.state, "user", None)  # Intenta obtener el usuario autenticado del estado de la request
    if user and hasattr(user, "id"):
        return str(user.id)  # Usa el id del usuario como clave
    return get_remote_address(request)  # Si no hay usuario, usa la IP como clave

# Crea una instancia global de Limiter usando la función de clave personalizada.
# Los límites específicos se configuran por endpoint usando decoradores.
limiter = Limiter(
    key_func=custom_key_func,
    default_limits=["100/minute"]  # Puedes setear este valor por defecto y ajustarlo con env vars
)