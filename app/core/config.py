from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Application ---
    app_name: str = "InventarioSaaS"
    app_env: str = Field(default="development")            # development, production, testing

    # --- Database ---
    database_url_async: str
    database_url_sync: str

    # --- Auth / Security ---
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # --- Rate limiting ---
    rate_limit_requests: int = 100
    rate_limit_minutes: int = 1

    # --- Logging ---
    log_level: str = "INFO"

    # --- Miscellaneous ---
    api_prefix: str = "/api/v1"
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # Asegura compatibilidad cross-platform
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
