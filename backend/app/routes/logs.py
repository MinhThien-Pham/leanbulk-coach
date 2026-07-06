from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dependencies import get_session
from backend.app.schemas import (
    BodyMetricLogRequest, WorkoutSetLogRequest, NutritionTargetLogRequest,
    MealLogRequest, SafetyFlagRequest
)
from backend.db.repositories import (
    add_body_metric_log, list_body_metric_logs, get_latest_body_metric,
    add_workout_set_log, list_workout_set_logs,
    add_nutrition_target_log, get_latest_nutrition_target,
    add_meal_log, list_meal_logs,
    add_safety_flag, list_open_safety_flags, resolve_safety_flag,
    get_user_profile
)
from backend.mcp_server.schemas import (
    dump_body_metric, dump_workout_set, dump_nutrition_target,
    dump_meal_log, dump_safety_flag
)

router = APIRouter(prefix="/logs", tags=["logs"])

async def _check_user(session: AsyncSession, user_id: int):
    user = await get_user_profile(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/body")
async def post_body(req: BodyMetricLogRequest, session: AsyncSession = Depends(get_session)):
    await _check_user(session, req.user_id)
    try:
        log = await add_body_metric_log(
            session, user_id=req.user_id, weight_kg=req.weight_kg, 
            waist_cm=req.waist_cm, notes=req.notes
        )
        await session.commit()
        return dump_body_metric(log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/body/{user_id}")
async def get_body_logs(user_id: int, limit: int = 30, session: AsyncSession = Depends(get_session)):
    await _check_user(session, user_id)
    logs = await list_body_metric_logs(session, user_id, limit)
    return [dump_body_metric(log) for log in logs]

@router.get("/body/{user_id}/latest")
async def get_latest_body(user_id: int, session: AsyncSession = Depends(get_session)):
    await _check_user(session, user_id)
    log = await get_latest_body_metric(session, user_id)
    if not log:
        raise HTTPException(status_code=404, detail="No body metric logs found")
    return dump_body_metric(log)

@router.post("/workouts")
async def post_workout(req: WorkoutSetLogRequest, session: AsyncSession = Depends(get_session)):
    await _check_user(session, req.user_id)
    try:
        log = await add_workout_set_log(
            session, user_id=req.user_id, exercise_name=req.exercise_name, 
            reps=req.reps, weight_kg=req.weight_kg, rir=req.rir, 
            muscle_group=req.muscle_group, set_number=req.set_number, notes=req.notes
        )
        await session.commit()
        return dump_workout_set(log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/workouts/{user_id}")
async def get_workout_logs(user_id: int, limit: int = 50, session: AsyncSession = Depends(get_session)):
    await _check_user(session, user_id)
    logs = await list_workout_set_logs(session, user_id, limit)
    return [dump_workout_set(log) for log in logs]

@router.post("/nutrition-targets")
async def post_nutrition_target(req: NutritionTargetLogRequest, session: AsyncSession = Depends(get_session)):
    await _check_user(session, req.user_id)
    try:
        log = await add_nutrition_target_log(
            session, user_id=req.user_id, target_kcal=req.target_kcal, 
            protein_g=req.protein_g, carbs_g=req.carbs_g, fat_g=req.fat_g, goal=req.goal
        )
        await session.commit()
        return dump_nutrition_target(log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/nutrition-targets/{user_id}/latest")
async def get_latest_nutrition_target_log(user_id: int, session: AsyncSession = Depends(get_session)):
    await _check_user(session, user_id)
    log = await get_latest_nutrition_target(session, user_id)
    if not log:
        raise HTTPException(status_code=404, detail="No nutrition target logs found")
    return dump_nutrition_target(log)

@router.post("/meals")
async def post_meal(req: MealLogRequest, session: AsyncSession = Depends(get_session)):
    await _check_user(session, req.user_id)
    try:
        log = await add_meal_log(
            session, user_id=req.user_id, meal_name=req.meal_name, kcal=req.kcal, 
            protein_g=req.protein_g, carbs_g=req.carbs_g, fat_g=req.fat_g, notes=req.notes
        )
        await session.commit()
        return dump_meal_log(log)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/meals/{user_id}")
async def get_meal_logs(user_id: int, limit: int = 50, session: AsyncSession = Depends(get_session)):
    await _check_user(session, user_id)
    logs = await list_meal_logs(session, user_id, limit)
    return [dump_meal_log(log) for log in logs]

@router.post("/safety-flags")
async def post_safety_flag(req: SafetyFlagRequest, session: AsyncSession = Depends(get_session)):
    await _check_user(session, req.user_id)
    try:
        flag = await add_safety_flag(
            session, user_id=req.user_id, flag_type=req.flag_type, 
            severity=req.severity, message=req.message
        )
        await session.commit()
        return dump_safety_flag(flag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/safety-flags/{user_id}/open")
async def get_open_flags(user_id: int, session: AsyncSession = Depends(get_session)):
    await _check_user(session, user_id)
    flags = await list_open_safety_flags(session, user_id)
    return [dump_safety_flag(flag) for flag in flags]

@router.post("/safety-flags/{flag_id}/resolve")
async def post_resolve_safety_flag(flag_id: int, session: AsyncSession = Depends(get_session)):
    try:
        flag = await resolve_safety_flag(session, flag_id)
        if not flag:
            raise HTTPException(status_code=404, detail="Safety flag not found")
        await session.commit()
        return dump_safety_flag(flag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
