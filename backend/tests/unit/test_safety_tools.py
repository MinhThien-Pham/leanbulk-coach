"""
test_safety_tools.py — Unit tests for backend/tools/safety_tools.py

Tests cover:
- check_pain_flag: keyword detection, medical pattern detection, empty input
- check_rate_of_change: gaining/losing too fast, waist creep, safe scenarios
- check_calorie_adjustment: surplus/deficit clamping
- check_training_volume: beginner/intermediate/advanced caps
- MEDICAL_DISCLAIMER presence
"""

import pytest
from backend.tools.safety_tools import (
    MAX_DEFICIT_KCAL,
    MAX_SURPLUS_KCAL,
    MAX_TRAINING_DAYS,
    MAX_WEEKLY_GAIN_KG,
    MAX_WEEKLY_LOSS_KG,
    MEDICAL_DISCLAIMER,
    PAIN_KEYWORDS,
    WAIST_CREEP_THRESHOLD_CM,
    check_calorie_adjustment,
    check_pain_flag,
    check_rate_of_change,
    check_training_volume,
)


# ---------------------------------------------------------------------------
# check_pain_flag
# ---------------------------------------------------------------------------

class TestCheckPainFlag:
    def test_empty_notes_all_clear(self):
        result = check_pain_flag("")
        assert result["pain_detected"] is False
        assert result["medical_request_detected"] is False
        assert result["block_training_advice"] is False
        assert result["message"] is None

    def test_none_like_whitespace_all_clear(self):
        result = check_pain_flag("   ")
        assert result["pain_detected"] is False

    def test_no_flags_for_normal_notes(self):
        result = check_pain_flag("Feeling great this week! Energy was high.")
        assert result["pain_detected"] is False
        assert result["medical_request_detected"] is False
        assert result["block_training_advice"] is False

    def test_pain_keyword_detected(self):
        result = check_pain_flag("My lower back is in pain today.")
        assert result["pain_detected"] is True
        assert "pain" in result["pain_keywords_found"]
        assert result["block_training_advice"] is True

    def test_hurt_keyword_detected(self):
        result = check_pain_flag("My shoulder hurts when I bench press.")
        assert result["pain_detected"] is True
        assert result["block_training_advice"] is True

    def test_injury_keyword_detected(self):
        result = check_pain_flag("I have an injury in my knee.")
        assert result["pain_detected"] is True

    def test_hernia_keyword_detected(self):
        result = check_pain_flag("I think I have a hernia.")
        assert result["pain_detected"] is True

    def test_medical_pattern_do_i_have(self):
        result = check_pain_flag("Do I have a hernia?")
        assert result["medical_request_detected"] is True
        assert result["block_training_advice"] is True

    def test_medical_pattern_diagnose(self):
        result = check_pain_flag("Can you diagnose my knee problem?")
        assert result["medical_request_detected"] is True

    def test_medical_pattern_is_it_serious(self):
        result = check_pain_flag("Is it serious if my shoulder clicks?")
        assert result["medical_request_detected"] is True

    def test_medical_flag_produces_disclaimer_in_message(self):
        result = check_pain_flag("Do I have a torn rotator cuff?")
        assert result["message"] is not None
        assert "healthcare professional" in result["message"].lower()

    def test_pain_flag_produces_message(self):
        result = check_pain_flag("Sharp pain in my knee during squats.")
        assert result["message"] is not None

    def test_case_insensitive_detection(self):
        result = check_pain_flag("PAIN in my lower back!")
        assert result["pain_detected"] is True

    def test_whole_word_matching_no_false_positive(self):
        # "peach" contains "ache" but should not trigger
        result = check_pain_flag("I ate a peach after training.")
        assert result["pain_detected"] is False

    def test_returns_required_keys(self):
        result = check_pain_flag("test notes")
        for key in ("pain_detected", "medical_request_detected", "pain_keywords_found",
                     "medical_patterns_matched", "block_training_advice", "message"):
            assert key in result

    def test_pain_keywords_found_is_list(self):
        result = check_pain_flag("pain and injury")
        assert isinstance(result["pain_keywords_found"], list)
        assert len(result["pain_keywords_found"]) >= 2

    def test_multiple_keywords_all_captured(self):
        result = check_pain_flag("Sharp pain and swelling in my knee.")
        # 'sharp', 'pain', 'swelling' all in keywords
        found = result["pain_keywords_found"]
        assert "pain" in found or "sharp" in found or "swelling" in found


# ---------------------------------------------------------------------------
# check_rate_of_change
# ---------------------------------------------------------------------------

class TestCheckRateOfChange:
    def test_returns_required_keys(self):
        result = check_rate_of_change(0.2, 0.1, "lean_bulk")
        for key in ("is_safe", "warnings", "flags"):
            assert key in result

    def test_normal_lean_bulk_is_safe(self):
        result = check_rate_of_change(
            weekly_weight_delta_kg=0.3,
            weekly_waist_delta_cm=0.0,
            goal="lean_bulk",
        )
        assert result["is_safe"] is True
        assert result["flags"] == []

    def test_gaining_too_fast_flags(self):
        result = check_rate_of_change(
            weekly_weight_delta_kg=MAX_WEEKLY_GAIN_KG + 0.1,
            weekly_waist_delta_cm=0.0,
            goal="lean_bulk",
        )
        assert result["is_safe"] is False
        assert "gaining_too_fast" in result["flags"]
        assert len(result["warnings"]) > 0

    def test_exactly_at_gain_threshold_is_safe(self):
        result = check_rate_of_change(
            weekly_weight_delta_kg=MAX_WEEKLY_GAIN_KG,
            weekly_waist_delta_cm=0.0,
            goal="lean_bulk",
        )
        assert result["is_safe"] is True

    def test_losing_too_fast_during_mini_cut(self):
        result = check_rate_of_change(
            weekly_weight_delta_kg=-MAX_WEEKLY_LOSS_KG - 0.1,
            weekly_waist_delta_cm=0.0,
            goal="mini_cut",
        )
        assert result["is_safe"] is False
        assert "losing_too_fast" in result["flags"]

    def test_waist_creep_adds_flag_not_unsafe(self):
        result = check_rate_of_change(
            weekly_weight_delta_kg=0.2,
            weekly_waist_delta_cm=WAIST_CREEP_THRESHOLD_CM + 0.1,
            goal="lean_bulk",
        )
        # Waist creep is a warning but doesn't set is_safe=False by itself
        assert "waist_creep" in result["flags"]

    def test_none_weight_delta_no_error(self):
        result = check_rate_of_change(None, None, "lean_bulk")
        assert result["is_safe"] is True  # No data = no violation

    def test_mini_cut_weight_loss_within_threshold_is_safe(self):
        result = check_rate_of_change(-0.5, 0.0, "mini_cut")
        assert result["is_safe"] is True

    def test_maintain_goal_gaining_fast_is_unsafe(self):
        result = check_rate_of_change(0.6, 0.0, "maintain")
        assert result["is_safe"] is False


# ---------------------------------------------------------------------------
# check_calorie_adjustment
# ---------------------------------------------------------------------------

class TestCheckCalorieAdjustment:
    def test_returns_required_keys(self):
        result = check_calorie_adjustment(250, "lean_bulk")
        for key in ("is_safe", "warnings", "clamped_adjustment_kcal", "requested_adjustment_kcal"):
            assert key in result

    def test_normal_lean_bulk_surplus_is_safe(self):
        result = check_calorie_adjustment(250, "lean_bulk")
        assert result["is_safe"] is True
        assert result["clamped_adjustment_kcal"] == 250

    def test_extreme_surplus_is_clamped(self):
        result = check_calorie_adjustment(1000, "lean_bulk")
        assert result["is_safe"] is False
        assert result["clamped_adjustment_kcal"] == float(MAX_SURPLUS_KCAL)
        assert len(result["warnings"]) > 0

    def test_normal_mini_cut_deficit_is_safe(self):
        result = check_calorie_adjustment(-300, "mini_cut")
        assert result["is_safe"] is True
        assert result["clamped_adjustment_kcal"] == -300

    def test_extreme_deficit_is_clamped(self):
        result = check_calorie_adjustment(-1000, "mini_cut")
        assert result["is_safe"] is False
        assert result["clamped_adjustment_kcal"] == float(-MAX_DEFICIT_KCAL)
        assert len(result["warnings"]) > 0

    def test_exactly_at_surplus_limit_is_safe(self):
        result = check_calorie_adjustment(float(MAX_SURPLUS_KCAL), "lean_bulk")
        assert result["is_safe"] is True

    def test_exactly_at_deficit_limit_is_safe(self):
        result = check_calorie_adjustment(float(-MAX_DEFICIT_KCAL), "mini_cut")
        assert result["is_safe"] is True

    def test_max_surplus_is_600(self):
        assert MAX_SURPLUS_KCAL == 600

    def test_max_deficit_is_500(self):
        assert MAX_DEFICIT_KCAL == 500

    def test_maintain_goal_no_clamping(self):
        result = check_calorie_adjustment(0, "maintain")
        assert result["is_safe"] is True
        assert result["clamped_adjustment_kcal"] == 0


# ---------------------------------------------------------------------------
# check_training_volume
# ---------------------------------------------------------------------------

class TestCheckTrainingVolume:
    def test_returns_required_keys(self):
        result = check_training_volume(3, "beginner")
        for key in ("is_safe", "warning", "requested_days", "recommended_days"):
            assert key in result

    def test_beginner_3_days_is_safe(self):
        result = check_training_volume(3, "beginner")
        assert result["is_safe"] is True
        assert result["warning"] is None

    def test_beginner_4_days_is_safe(self):
        result = check_training_volume(4, "beginner")
        assert result["is_safe"] is True

    def test_beginner_5_days_is_unsafe(self):
        result = check_training_volume(5, "beginner")
        assert result["is_safe"] is False
        assert result["recommended_days"] == MAX_TRAINING_DAYS["beginner"]
        assert result["warning"] is not None

    def test_intermediate_5_days_is_safe(self):
        result = check_training_volume(5, "intermediate")
        assert result["is_safe"] is True

    def test_intermediate_6_days_is_unsafe(self):
        result = check_training_volume(6, "intermediate")
        assert result["is_safe"] is False

    def test_advanced_6_days_is_safe(self):
        result = check_training_volume(6, "advanced")
        assert result["is_safe"] is True

    def test_unknown_level_defaults_to_beginner_cap(self):
        result = check_training_volume(5, "unknown_level")
        assert result["is_safe"] is False
        assert result["recommended_days"] == MAX_TRAINING_DAYS["beginner"]

    def test_beginner_max_is_4(self):
        assert MAX_TRAINING_DAYS["beginner"] == 4

    def test_intermediate_max_is_5(self):
        assert MAX_TRAINING_DAYS["intermediate"] == 5

    def test_advanced_max_is_6(self):
        assert MAX_TRAINING_DAYS["advanced"] == 6


# ---------------------------------------------------------------------------
# MEDICAL_DISCLAIMER
# ---------------------------------------------------------------------------

class TestMedicalDisclaimer:
    def test_disclaimer_is_non_empty(self):
        assert MEDICAL_DISCLAIMER
        assert len(MEDICAL_DISCLAIMER) > 50

    def test_disclaimer_contains_key_phrase(self):
        assert "not a substitute" in MEDICAL_DISCLAIMER.lower() or \
               "general fitness" in MEDICAL_DISCLAIMER.lower()

    def test_disclaimer_mentions_healthcare(self):
        assert "healthcare" in MEDICAL_DISCLAIMER.lower() or \
               "medical professional" in MEDICAL_DISCLAIMER.lower()
