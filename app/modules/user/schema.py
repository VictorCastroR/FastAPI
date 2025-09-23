from pydantic import BaseModel, EmailStr
from typing import Optional

# Datos que devuelve la API
class UserOut(BaseModel):
    id: int
    email: EmailStr
    slug: str
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True
        
# Datos que se reciben al crear usuario
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Datos que se reciben al actualizar usuario
class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    is_active: Optional[bool]