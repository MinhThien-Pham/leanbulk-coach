"""
calorie_tools.py — Deterministic calorie calculation tools for LeanBulk Coach.

All functions are pure (no I/O, no LLM calls, no side effects).
Units: weight in kg, height in cm, calories in kcal.
"""

from typing import Literal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Physical Activity Level (PAL) multipliers — Mifflin-St Jeor standard values
ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "sedentary": 1.2,           # Little or no exercise, desk job
    "lightly_active": 1.375,    # Light exercise 1–3 days/week
    "moderately_active": 1.55,  # Moderate exercise 3–5 days/week
    "very_active": 1.725,       # Hard exercise 6–7 days/week
    "extra_active": 1.9,        # Very hard exercise + physical job
}

# Conservative calorie adjustments for skinny-fat beginners
GOAL_ADJUSTMENTS_KCAL: dict[str, int] = {
    "lean_bulk": 250,    # Small surplus to minimize fat gain
    "lean_bulk_start": 200,  # Extra conservative for first-timers
    "mini_cut": -300,    # Modest deficit to preserve muscle
    "maintain": 0,
    "deload": 0,         # Maintain calories during deload week
}

# Absolute hard limits — enforced regardless of any calculation
CALORIE_FLOOR_KCAL = 1400
CALORIE_CEILING_KCAL = 6000


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def calc_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor equation.

    Args:
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        age: Age in years.
        sex: Biological sex — 'male' or 'female'.

    Returns:
        BMR in kilocalories per day (float, unrounded).

    Raises:
        ValueError: If sex is not 'male' or 'female', or if numeric inputs are <= 0.
    """
    if weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")
    if height_cm <= 0:
        raise ValueError("height_cm must be > 0")
    if age <= 0:
        raise ValueError("age must be > 0")

    sex_lower = sex.strip().lower()
    if sex_lower not in ("male", "female"):
        raise ValueError(f"sex must be 'male' or 'female', got: {sex!r}")
    if sex_lower == "male":
        return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age + 5.0
    else:
        return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age - 161.0


def calc_tdee(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
    activity_level: str,
) -> dict:
    """Calculate Total Daily Energy Expenditure (TDEE).

    Args:
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        age: Age in years.
        sex: 'male' or 'female'.
        activity_level: One of the keys in ACTIVITY_MULTIPLIERS.
            Defaults to 'lightly_active' if unrecognised.

    Returns:
        dict with keys:
            - bmr (int): Basal Metabolic Rate in kcal/day.
            - tdee (int): Total Daily Energy Expenditure in kcal/day.
            - activity_multiplier (float): PAL multiplier applied.
            - activity_level (str): Normalised activity level used.
    """
    activity_level = activity_level.strip().lower()
    if activity_level not in ACTIVITY_MULTIPLIERS:
        activity_level = "lightly_active"
        
    multiplier = ACTIVITY_MULTIPLIERS[activity_level]
    bmr = calc_bmr(weight_kg, height_cm, age, sex)
    tdee = bmr * multiplier
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "activity_multiplier": multiplier,
        "activity_level": activity_level,
    }


def calc_calorie_target(
    tdee: float,
    goal: Literal["lean_bulk", "lean_bulk_start", "mini_cut", "maintain", "deload"],
) -> dict:
    """Calculate the recommended daily calorie target for a given goal.

    Adjustments are conservative to suit skinny-fat beginners. The result
    is always clamped to [CALORIE_FLOOR_KCAL, CALORIE_CEILING_KCAL].

    Args:
        tdee: Total Daily Energy Expenditure in kcal/day.
        goal: One of 'lean_bulk', 'lean_bulk_start', 'mini_cut',
              'maintain', or 'deload'.

    Returns:
        dict with keys:
            - target_kcal (int): Recommended daily calorie intake.
            - adjustment_kcal (int): Surplus (+) or deficit (-) applied.
            - tdee (int): TDEE used in calculation.
            - goal (str): Goal used.
            - clamped (bool): True if the result was clamped to safe limits.
    """
    if tdee <= 0:
        raise ValueError("tdee must be > 0")

    goal = goal.strip().lower()
    if goal not in GOAL_ADJUSTMENTS_KCAL:
        raise ValueError(f"Invalid goal: {goal}")

    adjustment = GOAL_ADJUSTMENTS_KCAL[goal]
    raw_target = tdee + adjustment
    clamped_target = max(CALORIE_FLOOR_KCAL, min(raw_target, CALORIE_CEILING_KCAL))
    return {
        "target_kcal": round(clamped_target),
        "adjustment_kcal": adjustment,
        "tdee": round(tdee),
        "goal": goal,
        "clamped": clamped_target != raw_target,
    }
