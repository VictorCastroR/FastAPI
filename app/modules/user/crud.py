from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from typing import Optional

from fastapi_pagination.ext.sqlalchemy import paginate
from app.modules.user.model import User
from app.modules.user.schema import UserCreate, UserUpdate, UserOut
from app.modules.user.auth import hash_password
from app.core.helpers import generate_unique_slug, GenericPaginatedList


# ======================
# Crear usuario
# ======================
async def create_user(db: AsyncSession, user_in: UserCreate) -> UserOut:
    """
    Crea un nuevo usuario.
    Devuelve un schema UserOut para usar en responses.
    """
    hashed_pw = hash_password(user_in.password)
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
    return UserOut.model_validate(new_user)  # Convertimos a schema Pydantic


# ======================
# Obtener por ID
# ======================
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalars().first()
    if user:
        return user
    return None


# ======================
# Obtener por email
# ======================
async def get_user_by_email(db: AsyncSession, user_email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == user_email, User.is_active == True))
    user = result.scalars().first()
    if user:
        return user
    return None


# ======================
# Obtener por slug
# ======================
async def get_user_by_slug(db: AsyncSession, slug: str) -> Optional[UserOut]:
    result = await db.execute(select(User).where(User.slug == slug, User.is_active == True))
    user = result.scalars().first()
    if user:
        return UserOut.model_validate(user)
    return None


# ======================
# Listar usuarios (paginados + búsqueda)
# ======================
async def list_users(
    db: AsyncSession,
    search: Optional[str] = None,
) -> GenericPaginatedList[UserOut]:
    """
    Lista usuarios paginados.
    - Solo activos.
    - Busca por email o full_name si search está definido.
    """
    query = select(User).where(User.is_active == True)
    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )

    # paginate devuelve Page[User], pero usamos UserOut para el schema
    result = await paginate(db, query)
    # Convertir cada item a UserOut
    result.items = [UserOut.model_validate(u) for u in result.items]
    return result


# ======================
# Actualizar usuario
# ======================
async def update_user(
    db: AsyncSession,
    user: User,
    user_in: UserUpdate,
    regenerate_slug: bool = False
) -> UserUpdate:
    """
    Actualiza solo los campos que vienen no nulos en user_in y retorna UserUpdate.
    """

    # Diccionario dinámico de campos a actualizar
    update_data = user_in.model_dump(exclude_unset=True)

    # Manejo de password
    if "password" in update_data:
        user.hashed_password = hash_password(update_data.pop("password"))

    # Manejo de full_name y slug
    if "full_name" in update_data:
        user.full_name = update_data.pop("full_name")
        if regenerate_slug:
            user.slug = await generate_unique_slug(db, User, user.full_name)

    # Otros campos dinámicos
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Error al actualizar usuario")

    # Devuelve solo los campos actualizables
    return UserUpdate.model_validate(user)

# ======================
# Borrado lógico (soft delete)
# ======================
async def delete_user(db: AsyncSession, user: User) -> UserOut:
    """
    Soft delete: cambia is_active a False.
    """
    user.is_active = False
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise
    return UserOut.model_validate(user)
