"""
trend_tools.py — Deterministic trend analysis tools for LeanBulk Coach.

All functions are pure (no I/O, no LLM calls, no side effects).
Units: weight in kg, waist in cm, calories in kcal, protein in grams.
"""

from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Thresholds for classifying weight change direction
WEIGHT_GAINING_FAST_KG = 0.5   # > 0.5 kg/week = gaining fast
WEIGHT_GAINING_KG = 0.1        # 0.1–0.5 kg/week = gaining
WEIGHT_LOSING_FAST_KG = -0.5   # < -0.5 kg/week = losing fast
WEIGHT_LOSING_KG = -0.1        # -0.5 to -0.1 kg/week = losing

# Thresholds for waist trend
WAIST_INCREASING_FAST_CM = 0.5
WAIST_INCREASING_CM = 0.2
WAIST_DECREASING_FAST_CM = -0.5
WAIST_DECREASING_CM = -0.2

# Adherence flag threshold
LOW_ADHERENCE_PCT = 70.0


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def calc_7day_average(weights: list[Optional[float]]) -> Optional[float]:
    """Calculate the average of a list of daily weights, ignoring nulls/zeros.

    Args:
        weights: List of daily weight readings in kg. None or 0 values
            are treated as missing and excluded from the average.

    Returns:
        Average weight rounded to 2 decimal places, or None if no
        valid readings are present.
    """
    valid = [w for w in weights if w is not None and w > 0]
    if not valid:
        return None
    return round(sum(valid) / len(valid), 2)


def weight_trend(
    current_week_weights: list[Optional[float]],
    previous_week_weights: list[Optional[float]],
) -> dict:
    """Analyse weekly weight trend by comparing 7-day averages.

    Args:
        current_week_weights: Daily weight readings for the current week (kg).
        previous_week_weights: Daily weight readings for the previous week (kg).

    Returns:
        dict with keys:
            - current_avg_kg (float | None): 7-day average for current week.
            - previous_avg_kg (float | None): 7-day average for previous week.
            - delta_kg (float | None): Change in kg (positive = gained).
            - delta_lb (float | None): Change in pounds.
            - trend (str): One of 'gaining_fast', 'gaining', 'stable',
              'losing', 'losing_fast', 'insufficient_data'.
            - error (str | None): Set if current week data is missing.
    """
    current_avg = calc_7day_average(current_week_weights)
    if current_avg is None:
        return {
            "current_avg_kg": None,
            "previous_avg_kg": None,
            "delta_kg": None,
            "delta_lb": None,
            "trend": "insufficient_data",
            "error": "No valid weight readings for current week.",
        }

    previous_avg = calc_7day_average(previous_week_weights)
    delta_kg: Optional[float] = None
    delta_lb: Optional[float] = None
    trend = "insufficient_data"

    if previous_avg is not None:
        delta_kg = round(current_avg - previous_avg, 2)
        delta_lb = round(delta_kg * 2.20462, 2)

        if delta_kg > WEIGHT_GAINING_FAST_KG:
            trend = "gaining_fast"
        elif delta_kg > WEIGHT_GAINING_KG:
            trend = "gaining"
        elif delta_kg < WEIGHT_LOSING_FAST_KG:
            trend = "losing_fast"
        elif delta_kg < WEIGHT_LOSING_KG:
            trend = "losing"
        else:
            trend = "stable"

    return {
        "current_avg_kg": current_avg,
        "previous_avg_kg": previous_avg,
        "delta_kg": delta_kg,
        "delta_lb": delta_lb,
        "trend": trend,
        "error": None,
    }


def waist_trend(
    current_waist_cm: float,
    previous_waist_cm: Optional[float],
) -> dict:
    """Analyse weekly waist measurement trend.

    Args:
        current_waist_cm: Current waist measurement in cm.
        previous_waist_cm: Previous week's waist measurement in cm,
            or None if this is the first measurement.

    Returns:
        dict with keys:
            - current_cm (float): Current waist.
            - previous_cm (float | None): Previous waist.
            - delta_cm (float | None): Change in cm.
            - trend (str): One of 'increasing_fast', 'increasing',
              'stable', 'decreasing', 'decreasing_fast', 'baseline'.
    """
    if previous_waist_cm is None:
        return {
            "current_cm": current_waist_cm,
            "previous_cm": None,
            "delta_cm": None,
            "trend": "baseline",
        }

    delta_cm = round(current_waist_cm - previous_waist_cm, 1)

    if delta_cm > WAIST_INCREASING_FAST_CM:
        trend = "increasing_fast"
    elif delta_cm > WAIST_INCREASING_CM:
        trend = "increasing"
    elif delta_cm < WAIST_DECREASING_FAST_CM:
        trend = "decreasing_fast"
    elif delta_cm < WAIST_DECREASING_CM:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "current_cm": current_waist_cm,
        "previous_cm": previous_waist_cm,
        "delta_cm": delta_cm,
        "trend": trend,
    }


def adherence_score(
    actual_calories: float,
    target_calories: float,
    actual_protein_g: float,
    target_protein_g: float,
    workouts_completed: int,
    workouts_planned: int,
) -> dict:
    """Calculate adherence percentages for calories, protein, and workouts.

    Args:
        actual_calories: Average daily calories consumed this week (kcal).
        target_calories: Daily calorie target (kcal).
        actual_protein_g: Average daily protein consumed (g).
        target_protein_g: Daily protein target (g).
        workouts_completed: Number of workouts completed this week.
        workouts_planned: Number of workouts planned this week.

    Returns:
        dict with keys:
            - calorie_pct (float): Calorie adherence (0–200+%).
            - protein_pct (float): Protein adherence (0–200+%).
            - workout_pct (float): Workout adherence (0–100%).
            - overall_pct (float): Unweighted average of the three.
            - flags (list[str]): List of 'low_calorie_adherence',
              'low_protein_adherence', 'low_workout_adherence' for
              any metric below LOW_ADHERENCE_PCT.
            - is_low (bool): True if overall_pct < LOW_ADHERENCE_PCT.
    """
    cal_pct = round((actual_calories / target_calories) * 100, 1) if target_calories > 0 else 0.0
    protein_pct = round((actual_protein_g / target_protein_g) * 100, 1) if target_protein_g > 0 else 0.0
    workout_pct = round((workouts_completed / workouts_planned) * 100, 1) if workouts_planned > 0 else 0.0

    overall_pct = round((cal_pct + protein_pct + workout_pct) / 3, 1)

    flags: list[str] = []
    if cal_pct < LOW_ADHERENCE_PCT:
        flags.append("low_calorie_adherence")
    if protein_pct < LOW_ADHERENCE_PCT:
        flags.append("low_protein_adherence")
    if workout_pct < LOW_ADHERENCE_PCT:
        flags.append("low_workout_adherence")

    return {
        "calorie_pct": cal_pct,
        "protein_pct": protein_pct,
        "workout_pct": workout_pct,
        "overall_pct": overall_pct,
        "flags": flags,
        "is_low": overall_pct < LOW_ADHERENCE_PCT,
    }
