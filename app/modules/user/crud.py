from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from typing import Optional

from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_pagination import Page

from app.modules.user.model import User
from app.modules.user.schema import UserCreate, UserUpdate
from app.core.auth import hash_password
from app.core.helpers import generate_unique_slug


# ======================
# Crear usuario
# ======================
async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_pw = hash_password(user_in.password)

    # Generar slug único
    slug = await generate_unique_slug(db, User, user_in.full_name)

    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=user_in.is_superuser,
        slug=slug,
    )

    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("El email ya existe")
    await db.refresh(new_user)
    return new_user


# ======================
# Obtener por ID
# ======================
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


# ======================
# Obtener por slug
# ======================
async def get_user_by_slug(db: AsyncSession, slug: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.slug == slug))
    return result.scalars().first()


# ======================
# Obtener por email
# ======================
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


# ======================
# Listar usuarios (paginados + búsqueda)
# ======================
async def list_users(
    db: AsyncSession,
    search: Optional[str] = None,
) -> Page[User]:
    query = select(User)

    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )

    return await paginate(db, query)


# ======================
# Actualizar usuario
# ======================
async def update_user(db: AsyncSession, user: User, user_in: UserUpdate, regenerate_slug: bool = False) -> User:
    if user_in.password:
        user.hashed_password = hash_password(user_in.password)

    if user_in.full_name is not None:
        user.full_name = user_in.full_name
        if regenerate_slug:
            user.slug = await generate_unique_slug(db, User, user.full_name)

    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    if user_in.is_superuser is not None:
        user.is_superuser = user_in.is_superuser

    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise
    return user


# ======================
# Borrado lógico (soft delete)
# ======================
async def delete_user(db: AsyncSession, user: User) -> User:
    user.is_active = False
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise
    return user
