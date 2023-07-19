import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings as s

from src.models import Base

postgres_database_url = f'postgresql+asyncpg://{s.postgres_user}:{s.postgres_password}' \
                        f'@{s.postgres_host}:{s.postgres_port}/{s.postgres_db}'
engine = create_async_engine(postgres_database_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
    await engine.dispose()


async def database_create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main():
    pass


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
