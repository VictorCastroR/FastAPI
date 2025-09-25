from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_session
from app.core.helpers import GenericList, GenericPaginatedList
from app.modules.user import crud
from app.modules.user.schema import (
    UserCreate,
    UserUpdate,
    UserOut
)
from app.core.limiter import limiter  # si estás usando un rate limiter

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

# ======================
# Crear usuario
# ======================
@router.post("/", response_model=UserOut)
@limiter.limit("5/minute")
async def create_user_endpoint(user_in: UserCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        user = await crud.create_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ======================
# Listar usuarios paginados
# ======================
@router.get("/", response_model=GenericPaginatedList[UserOut])
@limiter.limit("10/minute")
async def list_users_endpoint(
    db: AsyncSession = Depends(get_async_session),
    search: Optional[str] = Query(None, description="Buscar por email o nombre")
):
    return await crud.list_users(db, search)


# ======================
# Obtener usuario por ID
# ======================
@router.get("/{user_id}", response_model=UserOut)
@limiter.limit("10/minute")
async def get_user_by_id_endpoint(user_id: int, db: AsyncSession = Depends(get_async_session)):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ======================
# Obtener usuario por slug
# ======================
@router.get("/slug/{slug}", response_model=UserOut)
@limiter.limit("10/minute")
async def get_user_by_slug_endpoint(slug: str, db: AsyncSession = Depends(get_async_session)):
    user = await crud.get_user_by_slug(db, slug)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ======================
# Actualizar usuario
# ======================
@router.put("/{user_id}", response_model=UserOut)
@limiter.limit("5/minute")
async def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    regenerate_slug: Optional[bool] = Query(False, description="Regenerar slug si se cambia full_name"),
    db: AsyncSession = Depends(get_async_session)
):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await crud.update_user(db, user, user_in, regenerate_slug)


# ======================
# Borrado lógico (soft delete)
# ======================
@router.delete("/{user_id}", response_model=UserOut)
@limiter.limit("3/minute")
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_async_session)):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await crud.delete_user(db, user)
