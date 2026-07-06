from datetime import datetime, timezone, timedelta
from backend.db.repositories import (
    create_user_profile,
    add_nutrition_target_log,
    add_body_metric_log,
    add_workout_set_log,
    add_meal_log,
    add_safety_flag
)
from backend.mcp_server.schemas import dump_user_profile
from backend.mcp_server.context_tools import (
    get_profile_context,
    get_latest_body_context,
    get_body_history_context,
    get_latest_nutrition_context,
    get_recent_workout_context,
    get_recent_meal_context,
    get_open_safety_context,
    get_progress_summary_context
)
from backend.workflows.coaching_summary import build_coaching_summary

async def seed_demo_profile(session) -> dict:
    # 1. Create a profile
    profile = await create_user_profile(
        session,
        display_name="Demo LeanBulk User",
        sex="male",
        age=25,
        height_cm=180.0,
        goal="lean_bulk",
        target_weight_kg=82.0
    )
    
    # 2. Add nutrition target
    await add_nutrition_target_log(
        session,
        user_id=profile.id,
        target_kcal=2700,
        protein_g=150,
        goal="lean_bulk"
    )
    
    # 3. Add at least 6 body metric logs across different days
    now = datetime.now(timezone.utc)
    body_logs_data = [
        {"weight_kg": 75.0, "waist_cm": 80.0, "days_ago": 6},
        {"weight_kg": 75.1, "waist_cm": 80.0, "days_ago": 5},
        {"weight_kg": 75.2, "waist_cm": 80.1, "days_ago": 4},
        {"weight_kg": 75.3, "waist_cm": 80.1, "days_ago": 3},
        {"weight_kg": 75.3, "waist_cm": 80.0, "days_ago": 2},
        {"weight_kg": 75.4, "waist_cm": 80.1, "days_ago": 1},
        {"weight_kg": 75.5, "waist_cm": 80.1, "days_ago": 0},
    ]
    
    for item in body_logs_data:
        logged_at = now - timedelta(days=item["days_ago"])
        await add_body_metric_log(
            session,
            user_id=profile.id,
            weight_kg=item["weight_kg"],
            waist_cm=item["waist_cm"],
            logged_at=logged_at,
            notes="Demo seeded metric"
        )
        
    # 4. Add at least 4 workout set logs
    workouts_data = [
        {"exercise_name": "Bench Press", "reps": 8, "weight_kg": 60.0, "rir": 2.0, "muscle_group": "chest"},
        {"exercise_name": "Chest-Supported Row", "reps": 10, "weight_kg": 50.0, "rir": 1.5, "muscle_group": "back"},
        {"exercise_name": "Romanian Deadlift", "reps": 8, "weight_kg": 80.0, "rir": 2.0, "muscle_group": "legs"},
        {"exercise_name": "Lateral Raise", "reps": 12, "weight_kg": 10.0, "rir": 1.0, "muscle_group": "shoulders"},
    ]
    
    for idx, item in enumerate(workouts_data):
        logged_at = now - timedelta(hours=(idx * 2))
        await add_workout_set_log(
            session,
            user_id=profile.id,
            exercise_name=item["exercise_name"],
            reps=item["reps"],
            weight_kg=item["weight_kg"],
            rir=item["rir"],
            muscle_group=item["muscle_group"],
            set_number=1,
            logged_at=logged_at,
            notes="Demo seeded workout set"
        )
        
    # 5. Add at least 3 meal logs
    meals_data = [
        {"meal_name": "Chicken and Rice", "kcal": 650, "protein_g": 45},
        {"meal_name": "Greek Yogurt Bowl", "kcal": 350, "protein_g": 30},
        {"meal_name": "Protein Shake", "kcal": 250, "protein_g": 30},
    ]
    
    for idx, item in enumerate(meals_data):
        logged_at = now - timedelta(hours=(idx * 3))
        await add_meal_log(
            session,
            user_id=profile.id,
            meal_name=item["meal_name"],
            kcal=item["kcal"],
            protein_g=item["protein_g"],
            logged_at=logged_at,
            notes="Demo seeded meal"
        )
        
    # 6. Add one open safety flag
    await add_safety_flag(
        session,
        user_id=profile.id,
        flag_type="pain_flag",
        severity="medium",
        message="Demo flag: user reported knee discomfort during squats.",
        logged_at=now
    )
    
    await session.commit()
    await session.refresh(profile)
    
    # Get contexts
    profile_ctx = await get_profile_context(session, profile.id)
    latest_body_ctx = await get_latest_body_context(session, profile.id)
    body_history_ctx = await get_body_history_context(session, profile.id)
    latest_nutrition_ctx = await get_latest_nutrition_context(session, profile.id)
    recent_workout_ctx = await get_recent_workout_context(session, profile.id)
    recent_meal_ctx = await get_recent_meal_context(session, profile.id)
    open_safety_ctx = await get_open_safety_context(session, profile.id)
    progress_summary_ctx = await get_progress_summary_context(session, profile.id)
    
    context = {
        "profile_context": profile_ctx,
        "latest_body_context": latest_body_ctx,
        "body_history_context": body_history_ctx,
        "latest_nutrition_context": latest_nutrition_ctx,
        "recent_workout_context": recent_workout_ctx,
        "recent_meal_context": recent_meal_ctx,
        "open_safety_context": open_safety_ctx,
        "progress_summary_context": progress_summary_ctx
    }
    
    # Get summary
    summary = build_coaching_summary(
        profile_context=profile_ctx,
        latest_body_context=latest_body_ctx,
        body_history_context=body_history_ctx,
        latest_nutrition_context=latest_nutrition_ctx,
        recent_workout_context=recent_workout_ctx,
        recent_meal_context=recent_meal_ctx,
        open_safety_context=open_safety_ctx,
        progress_summary_context=progress_summary_ctx
    )
    
    return {
        "demo_only": True,
        "profile": dump_user_profile(profile),
        "created": {
            "body_logs": len(body_logs_data),
            "workout_logs": len(workouts_data),
            "meal_logs": len(meals_data),
            "safety_flags": 1
        },
        "context": context,
        "summary": summary
    }
