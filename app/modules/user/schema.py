from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.core.helpers import GenericList, GenericPaginatedList

# ----------------------
# Schemas base
# ----------------------

class UserBase(BaseModel):
    """
    Datos básicos compartidos entre esquemas de usuario.
    """
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    full_name: str = Field(..., description="Nombre completo del usuario")
    is_active: bool = Field(True, description="Indica si el usuario está activo")
    is_superuser: Optional[bool] = Field(False, description="Indica si el usuario tiene permisos de superusuario")


class UserCreate(UserBase):
    """
    Esquema para creación de usuario.
    Incluye contraseña obligatoria.
    """
    password: str = Field(..., min_length=8, description="Contraseña del usuario (mínimo 8 caracteres)")


class UserUpdatePassword(BaseModel):
    """
    Para actualización de contraseña.
    """
    password: str = Field(..., min_length=8, description="Nueva contraseña del usuario")


class UserLogin(BaseModel):
    """
    Para login: email + password
    """
    email: EmailStr = Field(..., description="Correo electrónico para login")
    password: str = Field(..., description="Contraseña para login")


class UserUpdate(BaseModel):
    """
    Para actualizar parcialmente un usuario.
    Todos los campos opcionales.
    """
    email: Optional[EmailStr] = Field(None, description="Correo electrónico")
    full_name: Optional[str] = Field(None, description="Nombre completo")
    password: Optional[str] = Field(None, min_length=8, description="Contraseña")
    is_active: Optional[bool] = Field(None, description="Estado activo")
    is_superuser: Optional[bool] = Field(None, description="Permisos de superusuario")


# ----------------------
# Schemas de respuesta
# ----------------------

class UserOut(UserBase):
    """
    Esquema de salida para endpoints.
    Aquí usamos from_attributes=True para poder generar datos
    desde un modelo SQLAlchemy (User) con Pydantic v2.
    """

    id: int = Field(..., description="Identificador único del usuario")
    slug: str = Field(..., description="Slug único del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")

    model_config = {
        "from_attributes": True,          # Permite crear el schema a partir de un modelo SQLAlchemy
        "arbitrary_types_allowed": True,  # Necesario si usamos genéricos con modelos SQLAlchemy
    }


class UserList(GenericList[UserOut]):
    """
    Lista genérica de usuarios para respuestas sin paginación.
    """
    pass


class PaginatedUserList(GenericPaginatedList[UserOut]):
    """
    Lista paginada de usuarios con total, página y tamaño.
    Genérico usando UserOut para Pydantic v2.
    """
    pass


class ErrorResponse(BaseModel):
    """
    Para respuestas de error uniformes.
    """
    detail: str = Field(..., description="Mensaje de error")
