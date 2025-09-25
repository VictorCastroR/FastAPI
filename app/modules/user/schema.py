from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.core.helpers import GenericList, GenericPaginatedList

# ----------------------
# Schemas base
# ----------------------
class UserBase(BaseModel):
    """Datos básicos del usuario, compartidos en varios esquemas."""
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    full_name: str = Field(..., description="Nombre completo del usuario")
    is_active: bool = Field(True, description="Indica si el usuario está activo")
    is_superuser: Optional[bool] = Field(False, description="Indica si el usuario tiene permisos de superusuario")

class UserCreate(UserBase):
    """Datos necesarios para crear un usuario, incluye contraseña obligatoria."""
    password: str = Field(..., min_length=8, description="Contraseña del usuario (mínimo 8 caracteres)")

class UserUpdatePassword(BaseModel):
    """Esquema para actualizar la contraseña del usuario."""
    password: str = Field(..., min_length=8, description="Nueva contraseña del usuario (mínimo 8 caracteres)")

class UserLogin(BaseModel):
    """Esquema para login, incluye correo y contraseña."""
    email: EmailStr = Field(..., description="Correo electrónico para login")
    password: str = Field(..., description="Contraseña para login")

class UserUpdate(BaseModel):
    """Campos opcionales para actualización parcial del usuario."""
    email: Optional[EmailStr] = Field(None, description="Correo electrónico")
    full_name: Optional[str] = Field(None, description="Nombre completo")
    password: Optional[str] = Field(None, min_length=8, description="Contraseña")
    is_active: Optional[bool] = Field(None, description="Estado activo")
    is_superuser: Optional[bool] = Field(None, description="Permisos de superusuario")

# ----------------------
# Schemas de respuesta
# ----------------------
class UserOut(UserBase):
    """Datos devueltos en respuestas que incluyen información del usuario."""
    id: int = Field(..., description="Identificador único del usuario")
    slug: str = Field(..., description="Slug único del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")

    class Config:
        orm_mode = True

class UserList(GenericList[UserOut]):
    """Lista genérica de usuarios para respuestas sin paginación."""
    pass

class PaginatedUserList(GenericPaginatedList[UserOut]):
    """Lista paginada de usuarios con total, página y tamaño."""
    pass

class ErrorResponse(BaseModel):
    """Esquema para mensajes de error uniformes."""
    detail: str = Field(..., description="Mensaje de error")
