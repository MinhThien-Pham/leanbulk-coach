from datetime import datetime, timezone, timedelta
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db
from backend.db.repositories import (
    create_user_profile, add_nutrition_target_log, add_body_metric_log,
    add_workout_set_log, add_meal_log
)
from backend.tools.calorie_tools import calc_tdee, calc_calorie_target
from backend.tools.protein_tools import calc_protein_target
from backend.mcp_server.context_tools import (
    get_profile_context, get_latest_body_context, get_body_history_context,
    get_latest_nutrition_context, get_recent_workout_context, get_recent_meal_context,
    get_open_safety_context, get_progress_summary_context
)
from .coaching_summary import build_coaching_summary

async def run_local_demo_flow(database_url: str = "sqlite+aiosqlite:///:memory:") -> dict:
    engine = create_sqlite_async_engine(database_url)
    await init_db(engine)
    factory = create_async_session_factory(engine)
    
    try:
        async with factory() as session:
            # 1. create a demo user profile
            user = await create_user_profile(
                session, 
                display_name="Demo User", 
                sex="male", 
                age=25, 
                height_cm=183.0,
                goal="lean_bulk",
                target_weight_kg=84.0
            )
            
            # 2. calculate targets
            weight_kg = 75.0
            tdee_result = calc_tdee(weight_kg, 183.0, 25, "male", "moderately_active")
            cal_target_result = calc_calorie_target(tdee_result["tdee"], "lean_bulk")
            pro_target_result = calc_protein_target(weight_kg, "lean_bulk")
            
            cal_target = cal_target_result["target_kcal"]
            pro_target = pro_target_result["protein_g"]
            
            # 3. store nutrition target
            await add_nutrition_target_log(
                session,
                user_id=user.id,
                target_kcal=cal_target,
                protein_g=pro_target,
                carbs_g=0,
                fat_g=0,
                goal="lean_bulk"
            )
            
            # 4. add body metric logs (ordered)
            now = datetime.now(timezone.utc)
            await add_body_metric_log(session, user_id=user.id, weight_kg=75.0, waist_cm=80.0, logged_at=now - timedelta(days=4))
            await add_body_metric_log(session, user_id=user.id, weight_kg=75.1, waist_cm=80.0, logged_at=now - timedelta(days=3))
            await add_body_metric_log(session, user_id=user.id, weight_kg=75.2, waist_cm=80.1, logged_at=now - timedelta(days=2))
            await add_body_metric_log(session, user_id=user.id, weight_kg=75.3, waist_cm=80.1, logged_at=now - timedelta(days=1))
            
            # 5. add workout logs
            await add_workout_set_log(session, user_id=user.id, exercise_name="Bench Press", reps=8, weight_kg=60.0, rir=2)
            await add_workout_set_log(session, user_id=user.id, exercise_name="Bench Press", reps=7, weight_kg=60.0, rir=1)
            
            # 6. add meal logs
            await add_meal_log(session, user_id=user.id, meal_name="Chicken & Rice", kcal=600, protein_g=50)
            await add_meal_log(session, user_id=user.id, meal_name="Protein Shake", kcal=200, protein_g=30)
            
            # 7. read context back through MCP context tools
            contexts = {
                "profile_context": await get_profile_context(session, user.id),
                "latest_body_context": await get_latest_body_context(session, user.id),
                "body_history_context": await get_body_history_context(session, user.id),
                "latest_nutrition_context": await get_latest_nutrition_context(session, user.id),
                "recent_workout_context": await get_recent_workout_context(session, user.id),
                "recent_meal_context": await get_recent_meal_context(session, user.id),
                "open_safety_context": await get_open_safety_context(session, user.id),
                "progress_summary_context": await get_progress_summary_context(session, user.id)
            }
            
            # 8. generate summary
            summary = build_coaching_summary(**contexts)
            
            return {
                "profile": contexts["profile_context"],
                "contexts": contexts,
                "summary": summary,
                "metadata": {
                    "flow": "local_demo",
                    "live_llm_calls": False,
                    "database": "sqlite",
                    "activity_level": tdee_result["activity_level"]
                }
            }
    finally:
        await engine.dispose()
