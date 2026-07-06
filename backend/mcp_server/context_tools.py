from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.repositories import (
    get_user_profile,
    get_latest_body_metric,
    list_body_metric_logs,
    get_latest_nutrition_target,
    list_workout_set_logs,
    list_meal_logs,
    list_open_safety_flags
)
from backend.mcp_server.schemas import (
    dump_user_profile,
    dump_body_metric,
    dump_nutrition_target,
    dump_workout_set,
    dump_meal_log,
    dump_safety_flag
)
from backend.tools.trend_tools import weight_trend, waist_trend

def _validate_args(user_id: int, limit: int = 1):
    if user_id <= 0:
        raise ValueError("user_id must be > 0")
    if not (1 <= limit <= 100):
        raise ValueError("limit must be between 1 and 100")

async def get_profile_context(session: AsyncSession, user_id: int) -> dict:
    _validate_args(user_id)
    user = await get_user_profile(session, user_id)
    return dump_user_profile(user)

async def get_latest_body_context(session: AsyncSession, user_id: int) -> dict:
    _validate_args(user_id)
    log = await get_latest_body_metric(session, user_id)
    return dump_body_metric(log)

async def get_body_history_context(session: AsyncSession, user_id: int, limit: int = 30) -> list[dict]:
    _validate_args(user_id, limit)
    logs = await list_body_metric_logs(session, user_id, limit=limit)
    return [dump_body_metric(log) for log in logs]

async def get_latest_nutrition_context(session: AsyncSession, user_id: int) -> dict:
    _validate_args(user_id)
    log = await get_latest_nutrition_target(session, user_id)
    return dump_nutrition_target(log)

async def get_recent_workout_context(session: AsyncSession, user_id: int, limit: int = 50) -> list[dict]:
    _validate_args(user_id, limit)
    logs = await list_workout_set_logs(session, user_id, limit=limit)
    return [dump_workout_set(log) for log in logs]

async def get_recent_meal_context(session: AsyncSession, user_id: int, limit: int = 50) -> list[dict]:
    _validate_args(user_id, limit)
    logs = await list_meal_logs(session, user_id, limit=limit)
    return [dump_meal_log(log) for log in logs]

async def get_open_safety_context(session: AsyncSession, user_id: int) -> list[dict]:
    _validate_args(user_id)
    flags = await list_open_safety_flags(session, user_id)
    return [dump_safety_flag(f) for f in flags]

async def get_progress_summary_context(session: AsyncSession, user_id: int, limit: int = 14) -> dict:
    _validate_args(user_id, limit)
    logs = await list_body_metric_logs(session, user_id, limit=limit)
    
    if len(logs) < 2:
        return {
            "weight_trend": "insufficient_data", 
            "waist_trend": "insufficient_data",
            "sample_size": len(logs)
        }
    
    logs = list(reversed(logs)) # older first
    mid = len(logs) // 2
    prev = [log.weight_kg for log in logs[:mid]]
    curr = [log.weight_kg for log in logs[mid:]]
    
    w_trend = weight_trend(curr, prev)
    
    curr_waist = logs[-1].waist_cm
    prev_waist = logs[0].waist_cm
    
    if curr_waist is None or prev_waist is None:
        wa_trend = {"trend": "insufficient_data"}
    else:
        wa_trend = waist_trend(curr_waist, prev_waist)
        
    return {
        "weight_trend": w_trend.get("trend", "insufficient_data"),
        "waist_trend": wa_trend.get("trend", "insufficient_data"),
        "delta_kg": w_trend.get("delta_kg"),
        "delta_waist_cm": wa_trend.get("delta_cm") if 'delta_cm' in wa_trend else None,
        "sample_size": len(logs)
    }
