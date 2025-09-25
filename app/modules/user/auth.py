from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

from app.core.config import get_settings
from app.modules.user.model import RefreshToken

settings = get_settings()
pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__time_cost=2,
    argon2__memory_cost=102400,
    argon2__parallelism=8
)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hashea la contraseña usando Argon2."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(password, hashed)

def create_token(subject: str, expires_minutes: int, token_type: str = "access") -> str:
    """Crea un JWT para un subject con expiración y tipo dados."""
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": token_type
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token

def create_access_token(subject: str) -> str:
    """Crea un token de acceso."""
    return create_token(subject, settings.access_token_expire_minutes, token_type="access")

def create_refresh_token(subject: str) -> str:
    """Crea un token de refresco."""
    expires_minutes = settings.refresh_token_expire_days * 24 * 60
    return create_token(subject, expires_minutes, token_type="refresh")

async def save_refresh_token(db: AsyncSession, token: str, user_id: int, expires_at: datetime) -> RefreshToken:
    """Guarda un token de refresco en la base de datos."""
    db_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    try:
        await db.commit()
        await db.refresh(db_token)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error guardando refresh token: {e}")
        raise
    return db_token

async def validate_refresh_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
    """
    Valida que el token exista, no esté revocado y no haya expirado.
    Retorna la entidad RefreshToken si es válido, o None si no.
    """
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token, RefreshToken.revoked == False)
    )
    db_token = result.scalars().first()
    if not db_token:
        return None
    if db_token.expires_at < datetime.utcnow():
        db_token.revoked = True
        await db.commit()
        return None
    return db_token

def decode_token(token: str) -> Optional[dict]:
    """Decodifica cualquier JWT, retornando el payload o None si falla."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None

async def revoke_refresh_token(db: AsyncSession, token: str):
    """Revoca manualmente un token de refresco."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token)
    )
    db_token = result.scalars().first()
    if db_token:
        db_token.revoked = True
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Error al revocar refresh token: {e}")
            raise
