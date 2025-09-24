import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

def slugify(text: str) -> str:
    """Convierte un texto a formato slug básico"""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

async def generate_unique_slug(db: AsyncSession, model, base_text: str) -> str:
    base_slug = slugify(base_text)
    slug = base_slug
    index = 1

    while True:
        result = await db.execute(select(model).where(model.slug == slug))
        existing = result.scalars().first()
        if not existing:
            break
        slug = f"{base_slug}-{index:03d}"
        index += 1

    return slug
