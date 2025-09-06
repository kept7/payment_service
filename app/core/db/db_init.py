from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.auth_model import Base

from app.utils.config import settings


class DB:
    def __init__(self):
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
