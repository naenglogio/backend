import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.append(os.getcwd())
# 도메인 model registry를 로드해 각 도메인의 model.py가 Base.metadata에 등록되게 한다.
# (지금은 등록된 도메인 모델이 없어도 import 자체는 안전하다.)
import app.domains  # noqa: E402,F401
from app.core.config import settings
from app.db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Alembic은 동기 엔진을 사용하므로 asyncpg URL을 psycopg용으로 변환한다.
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg"),
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(
    object: object, name: str | None, type_: str, reflected: bool, compare_to: object
) -> bool:
    """CHECK 제약은 autogenerate 비교 대상에서 뺀다.

    Enum(native_enum=False, create_constraint=True)가 만드는 CHECK 제약은 SQLAlchemy가
    렌더링한 텍스트와 PostgreSQL이 reflect한 텍스트 표현이 미묘하게 달라, 실제로는
    바뀐 게 없어도 autogenerate가 매번 drop/create로 오탐지한다. enum 값 추가/삭제 같은
    CHECK 제약 변경은 항상 사람이 직접 migration을 작성해서 반영한다.
    """
    if type_ == "check_constraint":
        return False
    return True


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
        include_object=include_object,
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
        context.configure(
            connection=connection, target_metadata=target_metadata, include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
