from slugify import slugify as real_slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

def slugify(text: str) -> str:
    """Convierte un texto a slug-friendly usando python-slugify para internacionalización."""
    return real_slugify(text)

async def generate_unique_slug(db: AsyncSession, model, base_text: str, digits: int = 3) -> str:
    """
    Genera un slug único verificando existencia en modelo SQLAlchemy.

    Args:
        db (AsyncSession): sesión de la base de datos.
        model: modelo SQLAlchemy con atributo 'slug'.
        base_text (str): texto base para el slug.
        digits (int): cantidad de dígitos del sufijo incremental (default=3).

    Returns:
        str: slug único nunca repetido.
    """
    base_slug = slugify(base_text)
    slug = base_slug
    index = 1

    while True:
        result = await db.execute(select(model).where(model.slug == slug))
        existing = result.scalars().first()
        if not existing:
            break
        slug = f"{base_slug}-{index:0{digits}d}"
        index += 1

    return slug
