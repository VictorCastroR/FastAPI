from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from core.database import get_async_db
from core.limiter import limiter
from modules.user import schema, crud, auth

router = APIRouter(prefix="/users", tags=["Users"])

# ----------------------
# Registrar usuario
# ----------------------
@router.post("/", response_model=schema.UserOut)
async def create_user(user_in: schema.UserCreate, db: AsyncSession = Depends(get_async_db)):
    existing = await crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await crud.create_user(db, user_in.email, user_in.password)
    return user
