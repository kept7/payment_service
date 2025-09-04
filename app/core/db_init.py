from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.user_model import Base


class DB:
    def __init__(self, db_name: str):
        self.engine = create_async_engine(f"postgresql+asyncpg:///{db_name}")
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)