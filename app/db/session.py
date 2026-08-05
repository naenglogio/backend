from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# API 런타임은 asyncpg를 사용한다. migration(Alembic)은 별도로 psycopg 동기 드라이버를 쓴다.
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """요청마다 세션을 열고 요청 종료 시 닫는 FastAPI dependency.

    commit 경계는 이 dependency가 아니라 각 요청을 처리하는 service/repository가 명시적으로 정한다.
    """
    async with async_session_factory() as session:
        yield session
