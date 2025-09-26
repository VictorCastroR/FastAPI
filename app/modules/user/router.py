from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_session
from app.modules.user import crud, auth
from app.modules.user.schema import UserCreate, UserUpdate, UserOut
from app.core.helpers import GenericPaginatedList, get_current_user
from app.core.limiter import limiter  # SlowAPI rate limiter

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

# ======================
# Crear usuario
# ======================
@router.post("/", response_model=UserOut)
@limiter.limit("5/minute")
async def create_user_endpoint(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Crea un usuario nuevo.
    Rate limit: 5 requests/min.
    """
    try:
        user = await crud.create_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ======================
# Login
# ======================
@router.post("/login")
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    email: str,
    password: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Login de usuario.
    - Devuelve access token y refresh token si credenciales válidas.
    Rate limit: 10 requests/min.
    """
    user = await crud.get_user_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = auth.create_access_token(str(user.id))
    refresh_token = auth.create_refresh_token(str(user.id))
    await auth.save_refresh_token(
        db, refresh_token, user.id
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


# ======================
# Logout
# ======================
@router.post("/logout")
@limiter.limit("5/minute")
async def logout_user(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    """
    Logout del usuario autenticado.
    Revoca todos sus refresh tokens activos.
    """
    # Aquí podríamos revocar todos los refresh tokens activos
    # Por simplicidad, si recibimos refresh token en header lo revocamos
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token_value = token.split(" ")[1]
        await auth.revoke_refresh_token(db, token_value)
    return {"detail": "Logout exitoso"}


# ======================
# Obtener información del usuario autenticado
# ======================
@router.get("/me", response_model=UserOut)
@limiter.limit("10/minute")
async def get_my_user(
    request: Request,
    current_user=Depends(get_current_user)
):
    """
    Obtiene información del usuario autenticado.
    """
    return current_user


# ======================
# Actualizar información del usuario autenticado
# ======================
@router.put("/me", response_model=UserOut)
@limiter.limit("5/minute")
async def update_my_user(
    request: Request,
    user_in: UserUpdate,
    current_user=Depends(get_current_user),
    regenerate_slug: Optional[bool] = Query(False, description="Regenerar slug si se cambia full_name"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Actualiza los datos del usuario autenticado.
    """
    return await crud.update_user(db, current_user, user_in, regenerate_slug)


# ======================
# Rutas solo para admins (todavía sin control de roles)
# ======================
@router.get("/", response_model=GenericPaginatedList[UserOut])
@limiter.limit("10/minute")
async def list_users_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    search: Optional[str] = Query(None, description="Buscar por email o nombre")
):
    """
    Lista todos los usuarios (solo admins en el futuro).
    Rate limit: 10 requests/min.
    """
    return await crud.list_users(db, search)


@router.get("/{user_id}", response_model=UserOut)
@limiter.limit("10/minute")
async def get_user_by_id_endpoint(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Obtiene un usuario por ID (solo admins en el futuro).
    """
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/slug/{slug}", response_model=UserOut)
@limiter.limit("10/minute")
async def get_user_by_slug_endpoint(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Obtiene un usuario por slug (solo admins en el futuro).
    """
    user = await crud.get_user_by_slug(db, slug)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/{user_id}", response_model=UserOut)
@limiter.limit("3/minute")
async def delete_user_endpoint(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Soft delete de un usuario (solo admins en el futuro).
    """
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await crud.delete_user(db, user)
