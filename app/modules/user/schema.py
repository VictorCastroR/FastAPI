from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- Schemas base ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str              # Ahora es obligatorio
    is_active: bool = True      # Siempre inicia activo
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    password: str  # Obligatorio solo al crear

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# --- Schema para respuestas ---
class UserOut(UserBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True  # Permite retornar directamente objetos SQLAlchemy
