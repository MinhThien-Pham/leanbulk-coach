from typing import Callable, Dict
from backend.tools.calorie_tools import calc_bmr, calc_tdee, calc_calorie_target
from backend.tools.protein_tools import calc_protein_target
from backend.tools.meal_tools import suggest_meals
from backend.tools.progression_tools import suggest_linear_progression
from backend.tools.trend_tools import weight_trend, waist_trend
from backend.tools.safety_tools import check_rate_of_change, check_pain_flag, check_calorie_adjustment

def get_all_tools() -> Dict[str, Callable]:
    return {
        "calc_bmr": calc_bmr,
        "calc_tdee": calc_tdee,
        "calc_calorie_target": calc_calorie_target,
        "calc_protein_target": calc_protein_target,
        "suggest_meals": suggest_meals,
        "suggest_linear_progression": suggest_linear_progression,
        "weight_trend": weight_trend,
        "waist_trend": waist_trend,
        "check_rate_of_change": check_rate_of_change,
        "check_pain_flag": check_pain_flag,
        "check_calorie_adjustment": check_calorie_adjustment,
    }

def get_nutrition_tools() -> list[Callable]:
    registry = get_all_tools()
    return [
        registry["calc_bmr"],
        registry["calc_tdee"],
        registry["calc_calorie_target"],
        registry["calc_protein_target"],
        registry["suggest_meals"]
    ]

def get_training_tools() -> list[Callable]:
    registry = get_all_tools()
    return [
        registry["suggest_linear_progression"]
    ]

def get_progress_tools() -> list[Callable]:
    registry = get_all_tools()
    return [
        registry["weight_trend"],
        registry["waist_trend"]
    ]

def get_safety_tools() -> list[Callable]:
    registry = get_all_tools()
    return [
        registry["check_rate_of_change"],
        registry["check_pain_flag"],
        registry["check_calorie_adjustment"]
    ]
