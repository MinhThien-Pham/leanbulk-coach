import pytest
import pytest_asyncio
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db, drop_db
from backend.db.repositories import (
    create_user_profile, add_body_metric_log, add_workout_set_log, add_nutrition_target_log, add_meal_log
)
from backend.mcp_server.context_tools import (
    get_profile_context, get_latest_body_context, get_body_history_context,
    get_progress_summary_context, get_recent_workout_context, get_latest_nutrition_context,
    get_recent_meal_context, get_open_safety_context
)

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
async def test_invalid_args(session):
    with pytest.raises(ValueError, match="user_id must be > 0"):
        await get_profile_context(session, -1)
    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        await get_body_history_context(session, 1, limit=101)

@pytest.mark.asyncio
async def test_empty_user_returns_empty_dict(session):
    result = await get_profile_context(session, 999)
    assert result == {}

@pytest.mark.asyncio
async def test_context_tools_return_serializable_data(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    await add_body_metric_log(session, user_id=user.id, weight_kg=75.0, waist_cm=80.0)
    
    profile = await get_profile_context(session, user.id)
    assert isinstance(profile, dict)
    assert profile["display_name"] == "John"
    
    latest_body = await get_latest_body_context(session, user.id)
    assert isinstance(latest_body, dict)
    assert latest_body["weight_kg"] == 75.0
    
    body_history = await get_body_history_context(session, user.id)
    assert isinstance(body_history, list)
    assert len(body_history) == 1
    
    summary = await get_progress_summary_context(session, user.id)
    assert summary["weight_trend"] == "insufficient_data"
    assert summary["sample_size"] == 1

@pytest.mark.asyncio
async def test_progress_summary_with_data(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    await add_body_metric_log(session, user_id=user.id, weight_kg=75.0, waist_cm=80.0)
    await add_body_metric_log(session, user_id=user.id, weight_kg=75.5, waist_cm=80.5)
    
    summary = await get_progress_summary_context(session, user.id)
    assert "weight_trend" in summary
    assert "waist_trend" in summary
    assert summary["delta_waist_cm"] is not None
    assert summary["sample_size"] == 2

@pytest.mark.asyncio
async def test_progress_summary_missing_one_waist(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    await add_body_metric_log(session, user_id=user.id, weight_kg=75.0, waist_cm=80.0)
    await add_body_metric_log(session, user_id=user.id, weight_kg=75.5, waist_cm=None)
    
    summary = await get_progress_summary_context(session, user.id)
    assert summary["sample_size"] == 2
    assert summary["waist_trend"] == "insufficient_data"
    assert summary["delta_waist_cm"] is None

@pytest.mark.asyncio
async def test_other_contexts_return_correct_types(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    await add_workout_set_log(session, user_id=user.id, exercise_name="Squat", reps=5)
    await add_nutrition_target_log(session, user_id=user.id, target_kcal=2500, protein_g=150)
    await add_meal_log(session, user_id=user.id, meal_name="Chicken", kcal=300, protein_g=30)
    
    assert isinstance(await get_recent_workout_context(session, user.id), list)
    assert isinstance(await get_latest_nutrition_context(session, user.id), dict)
    assert isinstance(await get_recent_meal_context(session, user.id), list)
    assert isinstance(await get_open_safety_context(session, user.id), list)
