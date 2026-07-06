import pytest
import pytest_asyncio
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db, drop_db
from backend.db.repositories import (
    create_user_profile, get_user_profile, list_user_profiles,
    add_body_metric_log, get_latest_body_metric, list_body_metric_logs,
    add_workout_set_log, list_workout_set_logs,
    add_nutrition_target_log, get_latest_nutrition_target,
    add_meal_log, list_meal_logs,
    add_safety_flag, list_open_safety_flags, resolve_safety_flag
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
async def test_user_profile_crud(session):
    # Create
    user = await create_user_profile(
        session, display_name="John", sex="male", age=25, height_cm=180.0
    )
    assert user.id is not None
    
    # Get
    fetched = await get_user_profile(session, user.id)
    assert fetched.id == user.id
    
    # List
    users = await list_user_profiles(session)
    assert len(users) == 1

@pytest.mark.asyncio
async def test_user_profile_invalid(session):
    with pytest.raises(ValueError, match="age must be > 0"):
        await create_user_profile(session, display_name="John", sex="male", age=0, height_cm=180.0)
    with pytest.raises(ValueError, match="height_cm must be > 0"):
        await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=0)

@pytest.mark.asyncio
async def test_body_metric_logs(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    
    # Invalid
    with pytest.raises(ValueError, match="weight_kg must be > 0"):
        await add_body_metric_log(session, user_id=user.id, weight_kg=-5)
    with pytest.raises(ValueError, match="Invalid user_id"):
        await add_body_metric_log(session, user_id=999, weight_kg=75.0)
        
    # Add metrics
    log1 = await add_body_metric_log(session, user_id=user.id, weight_kg=75.0)
    log2 = await add_body_metric_log(session, user_id=user.id, weight_kg=76.0)
    
    # Get latest
    latest = await get_latest_body_metric(session, user.id)
    assert latest.id == log2.id
    
    # List (newest first)
    logs = await list_body_metric_logs(session, user.id)
    assert len(logs) == 2
    assert logs[0].id == log2.id

@pytest.mark.asyncio
async def test_workout_set_logs(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    
    with pytest.raises(ValueError, match="reps cannot be negative"):
        await add_workout_set_log(session, user_id=user.id, exercise_name="Squat", reps=-1)
    with pytest.raises(ValueError, match="Invalid user_id"):
        await add_workout_set_log(session, user_id=999, exercise_name="Squat", reps=5)
        
    log1 = await add_workout_set_log(session, user_id=user.id, exercise_name="Squat", reps=5)
    log2 = await add_workout_set_log(session, user_id=user.id, exercise_name="Squat", reps=5)
    
    logs = await list_workout_set_logs(session, user.id)
    assert len(logs) == 2
    assert logs[0].id == log2.id

@pytest.mark.asyncio
async def test_nutrition_target_logs(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    
    with pytest.raises(ValueError, match="target_kcal must be > 0"):
        await add_nutrition_target_log(session, user_id=user.id, target_kcal=0, protein_g=150)
        
    with pytest.raises(ValueError, match="protein_g cannot be negative"):
        await add_nutrition_target_log(session, user_id=user.id, target_kcal=2500, protein_g=-5)
    with pytest.raises(ValueError, match="Invalid user_id"):
        await add_nutrition_target_log(session, user_id=999, target_kcal=2500, protein_g=150)
        
    log = await add_nutrition_target_log(session, user_id=user.id, target_kcal=2500, protein_g=150)
    latest = await get_latest_nutrition_target(session, user.id)
    assert latest.id == log.id

@pytest.mark.asyncio
async def test_meal_logs(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    
    with pytest.raises(ValueError, match="kcal cannot be negative"):
        await add_meal_log(session, user_id=user.id, meal_name="Chicken", kcal=-1, protein_g=30)
        
    with pytest.raises(ValueError, match="protein_g cannot be negative"):
        await add_meal_log(session, user_id=user.id, meal_name="Chicken", kcal=300, protein_g=-1)
    with pytest.raises(ValueError, match="Invalid user_id"):
        await add_meal_log(session, user_id=999, meal_name="Chicken", kcal=300, protein_g=30)
        
    log = await add_meal_log(session, user_id=user.id, meal_name="Chicken", kcal=300, protein_g=30)
    logs = await list_meal_logs(session, user.id)
    assert len(logs) == 1
    assert logs[0].id == log.id

@pytest.mark.asyncio
async def test_safety_flags(session):
    user = await create_user_profile(session, display_name="John", sex="male", age=25, height_cm=180.0)
    
    with pytest.raises(ValueError, match="Invalid user_id"):
        await add_safety_flag(session, user_id=999, flag_type="waist_creep", severity="warning", message="msg")
        
    log = await add_safety_flag(session, user_id=user.id, flag_type="waist_creep", severity="warning", message="Waist growing fast")
    open_flags = await list_open_safety_flags(session, user.id)
    assert len(open_flags) == 1
    assert open_flags[0].id == log.id
    
    # Resolve it
    await resolve_safety_flag(session, log.id)
    open_flags = await list_open_safety_flags(session, user.id)
    assert len(open_flags) == 0
