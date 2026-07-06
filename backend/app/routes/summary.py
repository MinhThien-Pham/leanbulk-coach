from fastapi import APIRouter
from backend.app.schemas import SummaryRequest, SummaryResponse
from backend.workflows.coaching_summary import build_coaching_summary

router = APIRouter()

@router.post("/summary/build", response_model=SummaryResponse)
def post_summary_build(req: SummaryRequest):
    res = build_coaching_summary(
        profile_context=req.profile_context,
        latest_body_context=req.latest_body_context,
        body_history_context=req.body_history_context,
        latest_nutrition_context=req.latest_nutrition_context,
        recent_workout_context=req.recent_workout_context,
        recent_meal_context=req.recent_meal_context,
        open_safety_context=req.open_safety_context,
        progress_summary_context=req.progress_summary_context
    )
    return res
