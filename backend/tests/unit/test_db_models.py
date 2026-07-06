import pytest
import pytest_asyncio
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db, drop_db
from backend.db.models import UserProfile

@pytest_asyncio.fixture
async def engine():
    engine = create_sqlite_async_engine("sqlite+aiosqlite:///:memory:")
    await init_db(engine)
    yield engine
    await drop_db(engine)
    await engine.dispose()

@pytest_asyncio.fixture
async def session(engine):
    factory = create_async_session_factory(engine)
    async with factory() as session:
        yield session

@pytest.mark.asyncio
async def test_create_tables(engine, session):
    # Simply test that we can add and query a basic model
    user = UserProfile(display_name="Test", sex="male", age=25, height_cm=180.0)
    session.add(user)
    await session.commit()
    
    # Ensures no exception is thrown
    assert user.id is not None
