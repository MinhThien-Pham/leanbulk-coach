from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from backend.db.models import Base

def create_sqlite_async_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, echo=False)

def create_async_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False)

async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
