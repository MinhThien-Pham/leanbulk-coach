from backend.workflows.coaching_summary import build_coaching_summary

def test_coaching_summary_missing_profile():
    res = build_coaching_summary(
        profile_context={}, latest_body_context={}, body_history_context=[],
        latest_nutrition_context={}, recent_workout_context=[], recent_meal_context=[],
        open_safety_context=[], progress_summary_context={}
    )
    assert res["user_name"] is None
    assert "Complete intake profile" in res["next_actions"][0]
    
def test_coaching_summary_with_safety_flag():
    res = build_coaching_summary(
        profile_context={"display_name": "Test"}, latest_body_context={}, body_history_context=[],
        latest_nutrition_context={}, recent_workout_context=[], recent_meal_context=[],
        open_safety_context=[{"flag_type": "pain"}], progress_summary_context={}
    )
    assert res["safety_status"] == "attention_needed"
    assert any("Review open safety flags" in a for a in res["next_actions"])

def test_coaching_summary_empty_workout_meal():
    res = build_coaching_summary(
        profile_context={"display_name": "Test"}, latest_body_context={}, body_history_context=[],
        latest_nutrition_context={}, recent_workout_context=[], recent_meal_context=[],
        open_safety_context=[], progress_summary_context={}
    )
    assert "recommend logging workouts" in res["training_status"].lower()
    assert "recommend logging meals" in res["nutrition_status"].lower()

def test_coaching_summary_normal():
    res = build_coaching_summary(
        profile_context={"display_name": "Test", "goal": "lean_bulk"},
        latest_body_context={"weight_kg": 75.0, "waist_cm": 80.0},
        body_history_context=[{}],
        latest_nutrition_context={"target_kcal": 2500, "protein_g": 150},
        recent_workout_context=[{}],
        recent_meal_context=[{}],
        open_safety_context=[],
        progress_summary_context={"weight_trend": "gaining", "waist_trend": "stable"}
    )
    assert res["user_name"] == "Test"
    assert res["current_weight_kg"] == 75.0
    assert res["calorie_target_kcal"] == 2500
    assert "Keep following the plan" in res["next_actions"][0]
