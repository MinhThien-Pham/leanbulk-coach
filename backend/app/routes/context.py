from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dependencies import get_session
from backend.db.repositories import get_user_profile
from backend.mcp_server.context_tools import (
    get_profile_context, get_latest_body_context, get_body_history_context,
    get_latest_nutrition_context, get_recent_workout_context,
    get_recent_meal_context, get_open_safety_context, get_progress_summary_context
)

router = APIRouter(prefix="/context", tags=["context"])

@router.get("/{user_id}")
async def get_context(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await get_user_profile(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "profile_context": await get_profile_context(session, user_id),
        "latest_body_context": await get_latest_body_context(session, user_id),
        "body_history_context": await get_body_history_context(session, user_id),
        "latest_nutrition_context": await get_latest_nutrition_context(session, user_id),
        "recent_workout_context": await get_recent_workout_context(session, user_id),
        "recent_meal_context": await get_recent_meal_context(session, user_id),
        "open_safety_context": await get_open_safety_context(session, user_id),
        "progress_summary_context": await get_progress_summary_context(session, user_id)
    }
