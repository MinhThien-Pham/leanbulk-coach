"""
progression_tools.py — Deterministic workout progression tools for LeanBulk Coach.

All functions are pure (no I/O, no LLM calls, no side effects).
Implements simple linear progression appropriate for beginners.
Units: weight in kg, reps as integers.
"""

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default weight increments per exercise type
DEFAULT_INCREMENT_KG: dict[str, float] = {
    "squat": 2.5,
    "deadlift": 2.5,
    "bench_press": 2.5,
    "overhead_press": 1.25,
    "barbell_row": 2.5,
    "dumbbell": 1.0,
    "bodyweight": 0.0,  # Progress by reps or harder variant
    "default": 2.5,
}

DELOAD_LOAD_FACTOR = 0.5   # Reduce to 50% of working weight during deload

# Completion thresholds
STALL_CONSECUTIVE_WEEKS = 2  # Weeks of failed reps before considering stall


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def suggest_linear_progression(
    current_weight_kg: float,
    target_reps: int,
    reps_achieved: int,
    increment_kg: float = 2.5,
    deload_mode: bool = False,
) -> dict:
    """Recommend the next session's weight for a single lift using linear progression.

    Logic:
    - Deload mode: reduce to DELOAD_LOAD_FACTOR × current weight.
    - All reps achieved: increase by increment_kg.
    - Reps not achieved: repeat current weight, cue form focus.

    Args:
        current_weight_kg: Current working weight in kg.
        target_reps: Target rep count (e.g., 5 for 5×5 programmes).
        reps_achieved: Actual reps completed in the last set.
        increment_kg: Weight to add on a successful session (default 2.5 kg).
        deload_mode: If True, return 50% of current weight regardless of reps.

    Returns:
        dict with keys:
            - recommended_weight_kg (float): Next session's target weight.
            - recommended_reps (int): Target reps for next session.
            - progression_type (str): 'increase', 'repeat', or 'deload'.
            - achieved_all_reps (bool): Whether all target reps were hit.
            - note (str): Human-readable coaching note.
    """
    if deload_mode:
        deload_weight = round(current_weight_kg * DELOAD_LOAD_FACTOR, 2)
        return {
            "recommended_weight_kg": deload_weight,
            "recommended_reps": target_reps,
            "progression_type": "deload",
            "achieved_all_reps": reps_achieved >= target_reps,
            "note": (
                f"Deload week: use {deload_weight} kg × {target_reps} reps "
                "(50% of working weight). Focus on movement quality and recovery."
            ),
        }

    achieved = reps_achieved >= target_reps

    if achieved:
        new_weight = round(current_weight_kg + increment_kg, 2)
        return {
            "recommended_weight_kg": new_weight,
            "recommended_reps": target_reps,
            "progression_type": "increase",
            "achieved_all_reps": True,
            "note": (
                f"Great work! Increase to {new_weight} kg × {target_reps} reps "
                "next session."
            ),
        }
    else:
        return {
            "recommended_weight_kg": current_weight_kg,
            "recommended_reps": target_reps,
            "progression_type": "repeat",
            "achieved_all_reps": False,
            "note": (
                f"Repeat {current_weight_kg} kg × {target_reps} reps. "
                "Focus on controlled tempo and consistent form before adding weight."
            ),
        }


def suggest_weekly_progression(
    exercises: list[dict],
    deload_mode: bool = False,
) -> list[dict]:
    """Apply linear progression recommendations to a list of exercises.

    Each exercise dict should contain:
        - name (str): Exercise name (e.g. 'Squat').
        - current_weight_kg (float): Current working weight.
        - target_reps (int): Target reps per set.
        - reps_achieved (int): Reps completed in the last session.
        - increment_kg (float, optional): Weight increment. Default 2.5 kg.

    Args:
        exercises: List of exercise dicts (see above).
        deload_mode: If True, all exercises use deload protocol.

    Returns:
        List of progression recommendation dicts, each including 'exercise'
        key with the exercise name.
    """
    results = []
    for ex in exercises:
        result = suggest_linear_progression(
            current_weight_kg=float(ex.get("current_weight_kg", 0)),
            target_reps=int(ex.get("target_reps", 5)),
            reps_achieved=int(ex.get("reps_achieved", 0)),
            increment_kg=float(ex.get("increment_kg", DEFAULT_INCREMENT_KG["default"])),
            deload_mode=deload_mode,
        )
        result["exercise"] = ex.get("name", "Unknown Exercise")
        results.append(result)
    return results


def assess_strength_trend(
    weekly_completions: list[int],
    weekly_planned: int,
) -> dict:
    """Assess training consistency trend from recent workout completion history.

    Args:
        weekly_completions: List of workouts completed per week, most recent
            last. E.g. [3, 2, 3, 1] = four weeks, last week was 1.
        weekly_planned: Number of workouts planned per week (fixed).

    Returns:
        dict with keys:
            - trend (str): 'consistent', 'moderate', 'inconsistent',
              'very_inconsistent', or 'insufficient_data'.
            - avg_completion_pct (float | None): Average completion rate.
            - completion_pcts (list[float]): Per-week completion percentages.
            - stalled (bool): True if last 3 weeks were all below 70%.
    """
    if not weekly_completions or weekly_planned <= 0:
        return {
            "trend": "insufficient_data",
            "avg_completion_pct": None,
            "completion_pcts": [],
            "stalled": False,
        }

    pcts = [
        round((completions / weekly_planned) * 100, 1)
        for completions in weekly_completions
    ]
    avg = round(sum(pcts) / len(pcts), 1)

    if avg >= 90:
        trend = "consistent"
    elif avg >= 70:
        trend = "moderate"
    elif avg >= 50:
        trend = "inconsistent"
    else:
        trend = "very_inconsistent"

    # Stall detection: last STALL_CONSECUTIVE_WEEKS all below 70%
    stalled = (
        len(pcts) >= STALL_CONSECUTIVE_WEEKS
        and all(p < 70.0 for p in pcts[-STALL_CONSECUTIVE_WEEKS:])
    )

    return {
        "trend": trend,
        "avg_completion_pct": avg,
        "completion_pcts": pcts,
        "stalled": stalled,
    }
