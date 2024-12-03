from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# This import is needed for the alembic_postgresql_enum package to work
import alembic_postgresql_enum  # noqa: F401

if os.getenv("FLASK_ENV") != "migration":
    raise Exception(
        "This script should only be run in the migration environment. Please set the FLASK_ENV environment variable to 'migration'."
    )

from src.database import Base
import src.models.dailyorder
import src.models.employee
import src.models.group
import src.models.location
import src.models.oldorder
import src.models.person
import src.models.preorder
import src.models.user
import src.models.refresh_token_session  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

db_database = os.getenv("DB_DATABASE")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_password = os.getenv("DB_PASSWORD")


if not db_database or not db_user or not db_host or not db_port or not db_password:
    raise Exception(
        "Missing environment variables. Please run `docker compose run init` to create the .env file."
    )

config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}",
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
