def dump_user_profile(user) -> dict:
    if not user:
        return {}
    return {
        "id": user.id,
        "display_name": user.display_name,
        "sex": user.sex,
        "age": user.age,
        "height_cm": user.height_cm,
        "goal": user.goal,
        "target_weight_kg": user.target_weight_kg,
    }

def dump_body_metric(log) -> dict:
    if not log:
        return {}
    return {
        "id": log.id,
        "weight_kg": log.weight_kg,
        "waist_cm": log.waist_cm,
        "notes": log.notes,
    }

def dump_nutrition_target(log) -> dict:
    if not log:
        return {}
    return {
        "id": log.id,
        "target_kcal": log.target_kcal,
        "protein_g": log.protein_g,
        "carbs_g": log.carbs_g,
        "fat_g": log.fat_g,
        "goal": log.goal,
    }

def dump_workout_set(log) -> dict:
    if not log:
        return {}
    return {
        "id": log.id,
        "exercise_name": log.exercise_name,
        "reps": log.reps,
        "weight_kg": log.weight_kg,
        "rir": log.rir,
    }

def dump_meal_log(log) -> dict:
    if not log:
        return {}
    return {
        "id": log.id,
        "meal_name": log.meal_name,
        "kcal": log.kcal,
        "protein_g": log.protein_g,
    }

def dump_safety_flag(flag) -> dict:
    if not flag:
        return {}
    return {
        "id": flag.id,
        "flag_type": flag.flag_type,
        "severity": flag.severity,
        "message": flag.message,
    }
