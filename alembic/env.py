# ESTE ARCHIVO NO CUENTA COMO TAL, SE MODIFICA EL QUE ESTA DENTRO DE MIGRATIONS

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from app.core.config import get_settings
from app.core.database import Base
from app.modules.user.model import User, RefreshToken

# --- Configuración Alembic ---
config = context.config
fileConfig(config.config_file_name)

# Metadata de todos los modelos
target_metadata = Base.metadata

# --- Configuración desde Settings ---
settings = get_settings()
DATABASE_URL = settings.database_url_sync

# --- Modo offline ---
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# --- Modo online ---
def run_migrations_online():
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        future=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

# --- Ejecutar migraciones ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
