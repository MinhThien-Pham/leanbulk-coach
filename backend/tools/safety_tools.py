"""
safety_tools.py — Deterministic safety and guardrail tools for LeanBulk Coach.

All functions are pure (no I/O, no LLM calls, no side effects).
These tools MUST be called before any decision or training recommendation.

See specs/SECURITY_GUARDRAILS.md for the full guardrail architecture.
"""

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Pain and injury detection keywords (all lowercase)
PAIN_KEYWORDS: frozenset[str] = frozenset({
    "pain", "painful", "hurt", "hurts", "hurting", "injury", "injured",
    "sharp", "stabbing", "torn", "tear", "hernia", "strain", "sprain",
    "swelling", "swollen", "bruise", "bruising", "broken", "fracture",
    "dislocated", "popped", "snap", "snapped", "clicking", "grinding",
    "ache", "aching", "inflammation", "inflamed", "tendon", "tendinitis",
    "rotator", "pulled",
})

# Regex patterns that indicate a medical diagnosis request (all lowercase)
MEDICAL_DIAGNOSIS_PATTERNS: list[str] = [
    r"\bdo i have\b",
    r"\bam i\b.{0,30}\b(sick|ill|injured|broken|infected)\b",
    r"\bdiagnos(e|is|ed)\b",
    r"\bmedical condition\b",
    r"\bsymptom(s)?\b.{0,30}\b(mean|indicate|suggest|tell)\b",
    r"\bwhat is wrong with\b",
    r"\bis it (serious|dangerous|bad|broken|torn)\b",
    r"\bdo i need (surgery|an? (x-ray|mri|scan|doctor))\b",
]

# Rate-of-change safety thresholds
MAX_WEEKLY_GAIN_KG = 0.45    # ~1 lb/week — upper safe limit for lean bulk
MAX_WEEKLY_LOSS_KG = 0.90    # ~2 lb/week — upper safe limit for mini-cut
WAIST_CREEP_THRESHOLD_CM = 0.5  # cm/week trigger for mini-cut consideration

# Calorie adjustment safety limits
MAX_DEFICIT_KCAL = 500       # Never recommend > 500 kcal deficit for beginners
MAX_SURPLUS_KCAL = 600       # Never recommend > 600 kcal surplus for beginners

# Training volume caps by experience level
MAX_TRAINING_DAYS: dict[str, int] = {
    "beginner": 4,
    "intermediate": 5,
    "advanced": 6,
}

# Mandatory medical disclaimer text (injected in every response)
MEDICAL_DISCLAIMER = (
    "⚠️ Important: LeanBulk Coach provides general fitness guidance only and is not a "
    "substitute for professional medical advice, diagnosis, or treatment. Always consult "
    "a qualified healthcare professional before making significant changes to your diet or "
    "exercise program, especially if you have any pre-existing health conditions or injuries."
)


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def check_pain_flag(user_notes: str) -> dict:
    """Scan user notes for pain/injury keywords and medical diagnosis patterns.

    This is the primary guardrail for training advice. If pain or a medical
    request is detected, training advice MUST be withheld and a disclaimer
    issued.

    Args:
        user_notes: Free-text notes submitted by the user in their check-in.
            Empty string is safe.

    Returns:
        dict with keys:
            - pain_detected (bool): True if pain/injury keywords found.
            - medical_request_detected (bool): True if diagnosis-seeking language found.
            - pain_keywords_found (list[str]): Keywords that triggered the flag.
            - medical_patterns_matched (int): Number of medical regex patterns matched.
            - block_training_advice (bool): True if training advice should be blocked.
            - message (str | None): Human-readable safety message, or None if clear.
    """
    if not user_notes or not user_notes.strip():
        return {
            "pain_detected": False,
            "medical_request_detected": False,
            "pain_keywords_found": [],
            "medical_patterns_matched": 0,
            "block_training_advice": False,
            "message": None,
        }

    notes_lower = user_notes.lower()

    # Keyword scan — whole-word matching to avoid false positives (e.g. "ache" in "peach")
    pain_matches = [kw for kw in PAIN_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", notes_lower)]

    # Regex pattern scan
    medical_matches = sum(
        1 for pattern in MEDICAL_DIAGNOSIS_PATTERNS if re.search(pattern, notes_lower)
    )

    pain_detected = len(pain_matches) > 0
    medical_detected = medical_matches > 0
    block = pain_detected or medical_detected

    message: Optional[str] = None
    if medical_detected:
        message = (
            "⚠️ Medical Disclaimer: LeanBulk Coach cannot provide medical diagnoses or "
            "treat injuries. Please consult a qualified healthcare professional for "
            "any medical concerns. No training or nutrition changes are recommended "
            "until you have been cleared by a medical professional."
        )
    elif pain_detected:
        message = (
            "⚠️ Pain or discomfort detected in your notes. LeanBulk Coach cannot provide "
            "medical advice. If you are experiencing pain during exercise, please stop "
            "and consult a healthcare professional before resuming your training program."
        )

    return {
        "pain_detected": pain_detected,
        "medical_request_detected": medical_detected,
        "pain_keywords_found": pain_matches,
        "medical_patterns_matched": medical_matches,
        "block_training_advice": block,
        "message": message,
    }


def check_rate_of_change(
    weekly_weight_delta_kg: Optional[float],
    weekly_waist_delta_cm: Optional[float],
    goal: str,
) -> dict:
    """Check whether the current rate of weight and waist change is safe.

    Called before any decision output. A rate-of-change violation does NOT
    necessarily block the response but may change the recommended decision
    (e.g., switch to MINI_CUT if waist is creeping).

    Args:
        weekly_weight_delta_kg: Weight change this week vs last week (kg).
            Positive = gained, negative = lost. None if no previous data.
        weekly_waist_delta_cm: Waist change this week vs last week (cm).
            Positive = increased. None if no previous data.
        goal: Current goal — 'lean_bulk', 'mini_cut', 'maintain', 'deload'.

    Returns:
        dict with keys:
            - is_safe (bool): False if any safety threshold is breached.
            - warnings (list[str]): Human-readable warning messages.
            - flags (list[str]): Machine-readable flag codes.
    """
    warnings: list[str] = []
    flags: list[str] = []
    is_safe = True

    if weekly_weight_delta_kg is not None:
        if goal in ("lean_bulk", "lean_bulk_start", "maintain") and weekly_weight_delta_kg > MAX_WEEKLY_GAIN_KG:
            warnings.append(
                f"Weight is gaining too fast: +{weekly_weight_delta_kg:.2f} kg this week. "
                f"Target ≤ {MAX_WEEKLY_GAIN_KG} kg/week for a lean bulk. "
                "Consider reducing your calorie surplus slightly."
            )
            flags.append("gaining_too_fast")
            is_safe = False

        if goal == "mini_cut" and weekly_weight_delta_kg < -MAX_WEEKLY_LOSS_KG:
            warnings.append(
                f"Weight is dropping too fast: {weekly_weight_delta_kg:.2f} kg this week. "
                f"Target ≤ {MAX_WEEKLY_LOSS_KG} kg/week to preserve muscle mass. "
                "Consider increasing calories slightly."
            )
            flags.append("losing_too_fast")
            is_safe = False

    if weekly_waist_delta_cm is not None and weekly_waist_delta_cm > WAIST_CREEP_THRESHOLD_CM:
        warnings.append(
            f"Waist increased by +{weekly_waist_delta_cm:.1f} cm this week. "
            f"This exceeds the {WAIST_CREEP_THRESHOLD_CM} cm/week threshold. "
            "Consider a brief maintenance or mini-cut phase."
        )
        flags.append("waist_creep")
        # Waist creep is a warning, not automatically unsafe — decision agent handles it

    return {
        "is_safe": is_safe,
        "warnings": warnings,
        "flags": flags,
    }


def check_calorie_adjustment(requested_adjustment_kcal: float, goal: str) -> dict:
    """Validate that a requested calorie adjustment is within safe limits.

    Clamps the adjustment to the safe range and flags if clamping occurred.

    Args:
        requested_adjustment_kcal: The calorie adjustment the user or system
            wants to apply (negative = deficit, positive = surplus).
        goal: 'lean_bulk', 'mini_cut', 'maintain', or 'deload'.

    Returns:
        dict with keys:
            - is_safe (bool): False if the requested adjustment was outside limits.
            - warnings (list[str]): Explanation if adjustment was clamped.
            - clamped_adjustment_kcal (float): The safe adjustment to use.
            - requested_adjustment_kcal (float): The original request.
    """
    warnings: list[str] = []
    is_safe = True
    clamped = requested_adjustment_kcal

    if goal in ("lean_bulk", "lean_bulk_start") and requested_adjustment_kcal > MAX_SURPLUS_KCAL:
        warnings.append(
            f"Requested surplus of +{requested_adjustment_kcal:.0f} kcal/day exceeds the safe "
            f"limit of +{MAX_SURPLUS_KCAL} kcal/day for beginners. "
            "A large surplus leads to excess fat gain without additional muscle benefit."
        )
        clamped = float(MAX_SURPLUS_KCAL)
        is_safe = False

    if goal == "mini_cut" and requested_adjustment_kcal < -MAX_DEFICIT_KCAL:
        warnings.append(
            f"Requested deficit of {requested_adjustment_kcal:.0f} kcal/day exceeds the safe "
            f"limit of -{MAX_DEFICIT_KCAL} kcal/day. "
            "Aggressive deficits cause muscle loss and metabolic adaptation in beginners. "
            "Target a 200–300 kcal/day deficit instead."
        )
        clamped = float(-MAX_DEFICIT_KCAL)
        is_safe = False

    return {
        "is_safe": is_safe,
        "warnings": warnings,
        "clamped_adjustment_kcal": clamped,
        "requested_adjustment_kcal": requested_adjustment_kcal,
    }


def check_training_volume(days_per_week: int, training_level: str) -> dict:
    """Validate that the proposed training frequency is appropriate for the user.

    Args:
        days_per_week: Number of training days per week requested.
        training_level: 'beginner', 'intermediate', or 'advanced'.

    Returns:
        dict with keys:
            - is_safe (bool): False if days exceed level-appropriate max.
            - warning (str | None): Message if capped.
            - requested_days (int): Original request.
            - recommended_days (int): Safe recommended value.
    """
    level = training_level.strip().lower()
    max_days = MAX_TRAINING_DAYS.get(level, MAX_TRAINING_DAYS["beginner"])
    is_safe = days_per_week <= max_days

    warning: Optional[str] = None
    recommended = days_per_week if is_safe else max_days

    if not is_safe:
        warning = (
            f"Training {days_per_week} days/week may be excessive for a {level}. "
            f"The recommended maximum for a {level} is {max_days} days/week "
            "to allow adequate recovery and avoid overtraining."
        )

    return {
        "is_safe": is_safe,
        "warning": warning,
        "requested_days": days_per_week,
        "recommended_days": recommended,
    }
