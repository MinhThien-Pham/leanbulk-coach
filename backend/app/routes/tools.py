from fastapi import APIRouter, HTTPException
from backend.app.schemas import (
    CalorieTargetRequest, CalorieTargetResponse,
    ProteinTargetRequest, ProteinTargetResponse,
    MealSuggestionRequest, MealSuggestionResponse
)
from backend.tools.calorie_tools import calc_tdee, calc_calorie_target
from backend.tools.protein_tools import calc_protein_target
from backend.tools.meal_tools import suggest_meals

router = APIRouter()

@router.post("/tools/calorie-target", response_model=CalorieTargetResponse)
def post_calorie_target(req: CalorieTargetRequest):
    try:
        tdee_result = calc_tdee(req.weight_kg, req.height_cm, req.age, req.sex, req.activity_level)
        cal_result = calc_calorie_target(tdee_result["tdee"], req.goal)
        
        return {
            "bmr": tdee_result["bmr"],
            "tdee": tdee_result["tdee"],
            "activity_level": tdee_result["activity_level"],
            "target_kcal": cal_result["target_kcal"],
            "adjustment_kcal": cal_result["adjustment_kcal"],
            "goal": cal_result["goal"],
            "clamped": cal_result["clamped"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tools/protein-target", response_model=ProteinTargetResponse)
def post_protein_target(req: ProteinTargetRequest):
    try:
        res = calc_protein_target(req.weight_kg, req.goal)
        return {
            "protein_g": res["protein_g"],
            "protein_per_lb": res["protein_per_lb"],
            "goal": res["goal"],
            "clamped": res["clamped"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tools/meal-suggestions", response_model=MealSuggestionResponse)
def post_meal_suggestions(req: MealSuggestionRequest):
    try:
        res = suggest_meals(
            remaining_kcal=req.target_kcal,
            remaining_protein_g=req.target_protein_g,
            dietary_preferences=req.dietary_preferences,
            equipment_available=req.available_equipment,
            n_suggestions=req.n_suggestions
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
