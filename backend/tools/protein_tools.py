"""
protein_tools.py — Deterministic protein target tools for LeanBulk Coach.

All functions are pure (no I/O, no LLM calls, no side effects).
Units: weight in kg, protein in grams.
"""

from typing import Literal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Protein targets in grams per pound of bodyweight.
# Evidence base: 0.7–1.0g/lb is well-supported for natural trainees.
# Skinny-fat beginners: 0.82g/lb is conservative and achievable.
PROTEIN_RATES_G_PER_LB: dict[str, float] = {
    "lean_bulk": 0.82,       # Adequate for muscle protein synthesis
    "lean_bulk_start": 0.82,
    "mini_cut": 0.90,        # Slightly higher to preserve muscle during deficit
    "maintain": 0.82,
    "deload": 0.80,          # Can relax slightly; muscle not under high stress
}

KG_TO_LB = 2.20462

# Absolute bounds
PROTEIN_FLOOR_G = 100    # Below this is insufficient for any adult athlete
PROTEIN_CEILING_G = 350  # Beyond this is unnecessary and hard to eat


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def calc_protein_target(
    weight_kg: float,
    goal: Literal["lean_bulk", "lean_bulk_start", "mini_cut", "maintain", "deload"],
) -> dict:
    """Calculate the recommended daily protein intake.

    Uses goal-specific gram-per-pound rates appropriate for skinny-fat
    beginners. Result is clamped to [PROTEIN_FLOOR_G, PROTEIN_CEILING_G].

    Args:
        weight_kg: Body weight in kilograms.
        goal: One of 'lean_bulk', 'lean_bulk_start', 'mini_cut',
              'maintain', or 'deload'.

    Returns:
        dict with keys:
            - protein_g (int): Recommended daily protein in grams.
            - protein_per_lb (float): Rate used (g/lb).
            - protein_per_kg (float): Equivalent rate in g/kg.
            - weight_lb (float): Bodyweight in pounds.
            - weight_kg (float): Bodyweight in kilograms.
            - goal (str): Goal used.
            - clamped (bool): True if result was clamped to safe limits.
    """
    if weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")

    goal = goal.strip().lower()
    if goal not in PROTEIN_RATES_G_PER_LB:
        raise ValueError(f"Invalid goal: {goal}")

    rate_g_per_lb = PROTEIN_RATES_G_PER_LB[goal]
    weight_lb = weight_kg * KG_TO_LB
    raw_protein_g = weight_lb * rate_g_per_lb
    clamped_protein_g = max(PROTEIN_FLOOR_G, min(raw_protein_g, PROTEIN_CEILING_G))

    return {
        "protein_g": round(clamped_protein_g),
        "protein_per_lb": rate_g_per_lb,
        "protein_per_kg": round(rate_g_per_lb * KG_TO_LB, 2),
        "weight_lb": round(weight_lb, 1),
        "weight_kg": weight_kg,
        "goal": goal,
        "clamped": clamped_protein_g != raw_protein_g,
    }


def protein_from_food_sources(
    protein_g: float,
    weight_kg: float,
) -> dict:
    """Provide context on what the protein target means in food terms.

    A utility function to help the coach message explain the target
    in relatable terms. Values are rough equivalents only.

    Args:
        protein_g: Daily protein target in grams.
        weight_kg: Bodyweight in kilograms (used for context only).

    Returns:
        dict with:
            - protein_g (int): The target.
            - chicken_breast_g (int): Equivalent raw chicken breast.
            - eggs_approx (int): Approximate number of whole eggs.
            - greek_yogurt_g (int): Equivalent full-fat Greek yogurt.
    """
    # Rough protein densities (g protein per 100g food)
    chicken_per_100g = 31  # Raw chicken breast
    egg_protein_each = 6   # Whole egg
    yogurt_per_100g = 10   # Full-fat Greek yogurt

    return {
        "protein_g": round(protein_g),
        "chicken_breast_g": round((protein_g / chicken_per_100g) * 100),
        "eggs_approx": round(protein_g / egg_protein_each),
        "greek_yogurt_g": round((protein_g / yogurt_per_100g) * 100),
    }
