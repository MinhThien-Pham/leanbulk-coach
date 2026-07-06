def build_coaching_summary(
    *,
    profile_context: dict,
    latest_body_context: dict,
    body_history_context: list[dict],
    latest_nutrition_context: dict,
    recent_workout_context: list[dict],
    recent_meal_context: list[dict],
    open_safety_context: list[dict],
    progress_summary_context: dict,
) -> dict:
    if not profile_context:
        return {
            "user_name": None,
            "goal": None,
            "current_weight_kg": None,
            "latest_waist_cm": None,
            "calorie_target_kcal": None,
            "protein_target_g": None,
            "progress_status": "No profile found.",
            "safety_status": "unknown",
            "training_status": "unknown",
            "nutrition_status": "unknown",
            "next_actions": ["Complete intake profile to begin coaching."]
        }
        
    next_actions = []
    
    safety_status = "attention_needed" if open_safety_context else "clear"
    if open_safety_context:
        next_actions.append("Review open safety flags immediately.")
        
    w_trend = progress_summary_context.get("weight_trend", "insufficient_data")
    if w_trend == "insufficient_data":
        progress_status = "not enough trend data yet"
        next_actions.append("Log bodyweight daily to establish a trend.")
    else:
        progress_status = f"Weight trend: {w_trend}."
        
    if not recent_workout_context:
        training_status = "recommend logging workouts"
        next_actions.append("Log your first workout.")
    else:
        training_status = f"Logged {len(recent_workout_context)} recent workout sets."
        
    if not recent_meal_context:
        nutrition_status = "recommend logging meals"
        next_actions.append("Log your meals to ensure calorie/protein targets are met.")
    else:
        nutrition_status = f"Logged {len(recent_meal_context)} recent meals."
        
    if not next_actions:
        next_actions.append("Keep following the plan.")
        
    return {
        "user_name": profile_context.get("display_name"),
        "goal": profile_context.get("goal"),
        "current_weight_kg": latest_body_context.get("weight_kg") if latest_body_context else None,
        "latest_waist_cm": latest_body_context.get("waist_cm") if latest_body_context else None,
        "calorie_target_kcal": latest_nutrition_context.get("target_kcal") if latest_nutrition_context else None,
        "protein_target_g": latest_nutrition_context.get("protein_g") if latest_nutrition_context else None,
        "progress_status": progress_status,
        "safety_status": safety_status,
        "training_status": training_status,
        "nutrition_status": nutrition_status,
        "next_actions": next_actions
    }
