from slugify import slugify

def generate_slug(text: str, lowercase: bool = True) -> str:
    """
    Genera un slug para un texto dado.

    Args:
        text (str): Texto original a transformar.
        lowercase (bool): Convierte el resultado a minúsculas.

    Returns:
        str: Slug generado.
    """
    slug = slugify(text)
    if lowercase:
        return slug.lower()
    return slug
