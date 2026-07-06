from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models import (
    UserProfile, BodyMetricLog, WorkoutSetLog, NutritionTargetLog, MealLog, SafetyFlagLog
)

def _now_utc():
    return datetime.now(timezone.utc)

async def create_user_profile(
    session: AsyncSession, *, display_name, sex, age, height_cm, goal="lean_bulk", target_weight_kg=None
) -> UserProfile:
    if age <= 0:
        raise ValueError("age must be > 0")
    if height_cm <= 0:
        raise ValueError("height_cm must be > 0")
        
    profile = UserProfile(
        display_name=display_name, sex=sex, age=age, height_cm=height_cm,
        goal=goal, target_weight_kg=target_weight_kg
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile

async def get_user_profile(session: AsyncSession, user_id: int) -> UserProfile | None:
    result = await session.execute(select(UserProfile).where(UserProfile.id == user_id))
    return result.scalar_one_or_none()

async def list_user_profiles(session: AsyncSession) -> list[UserProfile]:
    result = await session.execute(select(UserProfile))
    return list(result.scalars().all())

async def add_body_metric_log(
    session: AsyncSession, *, user_id, weight_kg, waist_cm=None, logged_at=None, notes=None
) -> BodyMetricLog:
    if weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")
        
    if not await get_user_profile(session, user_id):
        raise ValueError(f"Invalid user_id: {user_id}")
        
    log = BodyMetricLog(
        user_id=user_id, weight_kg=weight_kg, waist_cm=waist_cm,
        logged_at=logged_at or _now_utc(), notes=notes
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

async def get_latest_body_metric(session: AsyncSession, user_id: int) -> BodyMetricLog | None:
    result = await session.execute(
        select(BodyMetricLog)
        .where(BodyMetricLog.user_id == user_id)
        .order_by(BodyMetricLog.logged_at.desc(), BodyMetricLog.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def list_body_metric_logs(session: AsyncSession, user_id: int, limit: int = 30) -> list[BodyMetricLog]:
    result = await session.execute(
        select(BodyMetricLog)
        .where(BodyMetricLog.user_id == user_id)
        .order_by(BodyMetricLog.logged_at.desc(), BodyMetricLog.id.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

async def add_workout_set_log(
    session: AsyncSession, *, user_id, exercise_name, reps, weight_kg=None, rir=None, 
    muscle_group=None, set_number=None, logged_at=None, notes=None
) -> WorkoutSetLog:
    if reps < 0:
        raise ValueError("reps cannot be negative")
        
    if not await get_user_profile(session, user_id):
        raise ValueError(f"Invalid user_id: {user_id}")

    log = WorkoutSetLog(
        user_id=user_id, exercise_name=exercise_name, reps=reps, weight_kg=weight_kg,
        rir=rir, muscle_group=muscle_group, set_number=set_number,
        logged_at=logged_at or _now_utc(), notes=notes
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

async def list_workout_set_logs(session: AsyncSession, user_id: int, limit: int = 50) -> list[WorkoutSetLog]:
    result = await session.execute(
        select(WorkoutSetLog)
        .where(WorkoutSetLog.user_id == user_id)
        .order_by(WorkoutSetLog.logged_at.desc(), WorkoutSetLog.id.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

async def add_nutrition_target_log(
    session: AsyncSession, *, user_id, target_kcal, protein_g, carbs_g=None, fat_g=None, 
    goal="lean_bulk", logged_at=None
) -> NutritionTargetLog:
    if target_kcal <= 0:
        raise ValueError("target_kcal must be > 0")
    if protein_g < 0:
        raise ValueError("protein_g cannot be negative")
        
    if not await get_user_profile(session, user_id):
        raise ValueError(f"Invalid user_id: {user_id}")
        
    log = NutritionTargetLog(
        user_id=user_id, target_kcal=target_kcal, protein_g=protein_g,
        carbs_g=carbs_g, fat_g=fat_g, goal=goal, logged_at=logged_at or _now_utc()
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

async def get_latest_nutrition_target(session: AsyncSession, user_id: int) -> NutritionTargetLog | None:
    result = await session.execute(
        select(NutritionTargetLog)
        .where(NutritionTargetLog.user_id == user_id)
        .order_by(NutritionTargetLog.logged_at.desc(), NutritionTargetLog.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def add_meal_log(
    session: AsyncSession, *, user_id, meal_name, kcal, protein_g, carbs_g=None, fat_g=None, 
    logged_at=None, notes=None
) -> MealLog:
    if kcal < 0:
        raise ValueError("kcal cannot be negative")
    if protein_g < 0:
        raise ValueError("protein_g cannot be negative")
        
    if not await get_user_profile(session, user_id):
        raise ValueError(f"Invalid user_id: {user_id}")
        
    log = MealLog(
        user_id=user_id, meal_name=meal_name, kcal=kcal, protein_g=protein_g,
        carbs_g=carbs_g, fat_g=fat_g, logged_at=logged_at or _now_utc(), notes=notes
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

async def list_meal_logs(session: AsyncSession, user_id: int, limit: int = 50) -> list[MealLog]:
    result = await session.execute(
        select(MealLog)
        .where(MealLog.user_id == user_id)
        .order_by(MealLog.logged_at.desc(), MealLog.id.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

async def add_safety_flag(
    session: AsyncSession, *, user_id, flag_type, severity, message, logged_at=None
) -> SafetyFlagLog:
    if not await get_user_profile(session, user_id):
        raise ValueError(f"Invalid user_id: {user_id}")
        
    log = SafetyFlagLog(
        user_id=user_id, flag_type=flag_type, severity=severity, message=message,
        logged_at=logged_at or _now_utc()
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

async def list_open_safety_flags(session: AsyncSession, user_id: int) -> list[SafetyFlagLog]:
    result = await session.execute(
        select(SafetyFlagLog)
        .where(SafetyFlagLog.user_id == user_id, SafetyFlagLog.resolved == False)
        .order_by(SafetyFlagLog.logged_at.desc(), SafetyFlagLog.id.desc())
    )
    return list(result.scalars().all())

async def resolve_safety_flag(session: AsyncSession, flag_id: int) -> SafetyFlagLog | None:
    result = await session.execute(select(SafetyFlagLog).where(SafetyFlagLog.id == flag_id))
    flag = result.scalar_one_or_none()
    if flag:
        flag.resolved = True
        await session.commit()
        await session.refresh(flag)
    return flag
