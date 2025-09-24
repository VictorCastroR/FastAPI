# test_db_url.py
from app.core.config import get_settings

settings = get_settings()
print(settings.database_url_sync)
