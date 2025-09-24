from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import get_settings
from modules.user.model import RefreshToken

settings = get_settings()

# ----------------------
# Password hashing
# ----------------------
pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__time_cost=2,
    argon2__memory_cost=102400,
    argon2__parallelism=8
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ----------------------
# Token creation
# ----------------------
def create_token(subject: str, expires_minutes: int, token_type: str = "access") -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": token_type
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token

def create_access_token(subject: str) -> str:
    return create_token(subject, settings.access_token_expire_minutes, token_type="access")

def create_refresh_token(subject: str) -> str:
    # Expiración en minutos
    expires_minutes = settings.refresh_token_expire_days * 24 * 60
    return create_token(subject, expires_minutes, token_type="refresh")

# ----------------------
# Save refresh token in DB
# ----------------------
async def save_refresh_token(db: AsyncSession, token: str, user_id: int, expires_at: datetime) -> RefreshToken:
    db_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token

# ----------------------
# Validate refresh token
# ----------------------
async def validate_refresh_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token, RefreshToken.revoked == False)
    )
    db_token = result.scalars().first()
    if not db_token:
        return None  # token inválido o revocado
    if db_token.expires_at < datetime.utcnow():
        db_token.revoked = True
        await db.commit()
        return None
    return db_token

# ----------------------
# Decode any JWT
# ----------------------
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None

# ----------------------
# Revoke a refresh token manually
# ----------------------
async def revoke_refresh_token(db: AsyncSession, token: str):
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token)
    )
    db_token = result.scalars().first()
    if db_token:
        db_token.revoked = True
        await db.commit()
