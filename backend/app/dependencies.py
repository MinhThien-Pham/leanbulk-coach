import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db

def get_database_url() -> str:
    return os.environ.get("LEANBULK_DATABASE_URL", "sqlite+aiosqlite:///./leanbulk_api.db")

_engine = None
_session_maker = None

def get_app_engine(database_url: str | None = None):
    global _engine, _session_maker
    if _engine is None:
        if database_url is None:
            database_url = get_database_url()
        _engine = create_sqlite_async_engine(database_url)
        _session_maker = create_async_session_factory(_engine)
    return _engine

async def init_app_database(database_url: str | None = None):
    engine = get_app_engine(database_url)
    await init_db(engine)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    global _session_maker
    if _session_maker is None:
        get_app_engine()
    
    async with _session_maker() as session:
        yield session
