"""
test_calorie_tools.py — Unit tests for backend/tools/calorie_tools.py

Tests cover:
- BMR formula correctness (male and female)
- TDEE with all activity levels
- Calorie target for all goals
- Floor and ceiling clamping
- Edge cases (borderline values, unknown activity level)
"""

import pytest
from backend.tools.calorie_tools import (
    ACTIVITY_MULTIPLIERS,
    CALORIE_CEILING_KCAL,
    CALORIE_FLOOR_KCAL,
    GOAL_ADJUSTMENTS_KCAL,
    calc_bmr,
    calc_calorie_target,
    calc_tdee,
)


# ---------------------------------------------------------------------------
# calc_bmr
# ---------------------------------------------------------------------------

class TestCalcBmr:
    def test_male_formula(self):
        # Mifflin-St Jeor male: 10w + 6.25h - 5a + 5
        result = calc_bmr(weight_kg=75, height_cm=175, age=25, sex="male")
        expected = 10 * 75 + 6.25 * 175 - 5 * 25 + 5  # = 1818.75
        assert abs(result - expected) < 0.01

    def test_female_formula(self):
        # Mifflin-St Jeor female: 10w + 6.25h - 5a - 161
        result = calc_bmr(weight_kg=60, height_cm=165, age=30, sex="female")
        expected = 10 * 60 + 6.25 * 165 - 5 * 30 - 161  # = 1370.25
        assert abs(result - expected) < 0.01

    def test_case_insensitive_sex(self):
        assert calc_bmr(70, 170, 25, "Male") == calc_bmr(70, 170, 25, "male")
        assert calc_bmr(70, 170, 25, "FEMALE") == calc_bmr(70, 170, 25, "female")

    def test_sex_with_whitespace(self):
        assert calc_bmr(70, 170, 25, " male ") == calc_bmr(70, 170, 25, "male")

    def test_invalid_sex_raises(self):
        with pytest.raises(ValueError, match="sex must be 'male' or 'female'"):
            calc_bmr(70, 170, 25, "other")

    def test_invalid_numeric_inputs_raise(self):
        with pytest.raises(ValueError, match="weight_kg must be > 0"):
            calc_bmr(0, 170, 25, "male")
        with pytest.raises(ValueError, match="height_cm must be > 0"):
            calc_bmr(70, -1, 25, "male")
        with pytest.raises(ValueError, match="age must be > 0"):
            calc_bmr(70, 170, 0, "male")

    def test_higher_weight_increases_bmr(self):
        lighter = calc_bmr(60, 170, 25, "male")
        heavier = calc_bmr(90, 170, 25, "male")
        assert heavier > lighter

    def test_older_age_decreases_bmr(self):
        young = calc_bmr(75, 175, 20, "male")
        old = calc_bmr(75, 175, 50, "male")
        assert old < young

    def test_taller_height_increases_bmr(self):
        short = calc_bmr(75, 160, 25, "male")
        tall = calc_bmr(75, 185, 25, "male")
        assert tall > short

    def test_male_vs_female_same_stats(self):
        # Male should be higher than female (males get +5, females get -161)
        male = calc_bmr(70, 170, 25, "male")
        female = calc_bmr(70, 170, 25, "female")
        assert male - female == pytest.approx(166.0, abs=0.01)


# ---------------------------------------------------------------------------
# calc_tdee
# ---------------------------------------------------------------------------

class TestCalcTdee:
    def test_returns_required_keys(self):
        result = calc_tdee(75, 175, 25, "male", "moderately_active")
        assert "bmr" in result
        assert "tdee" in result
        assert "activity_multiplier" in result
        assert "activity_level" in result

    def test_all_activity_levels_produce_different_tdee(self):
        tdeees = set()
        for level in ACTIVITY_MULTIPLIERS:
            r = calc_tdee(75, 175, 25, "male", level)
            tdeees.add(r["tdee"])
        assert len(tdeees) == len(ACTIVITY_MULTIPLIERS)

    def test_sedentary_is_lowest(self):
        sedentary = calc_tdee(75, 175, 25, "male", "sedentary")["tdee"]
        very_active = calc_tdee(75, 175, 25, "male", "very_active")["tdee"]
        assert sedentary < very_active

    def test_unknown_activity_level_defaults_to_lightly_active(self):
        unknown = calc_tdee(75, 175, 25, "male", "unknown_level")
        lightly = calc_tdee(75, 175, 25, "male", "lightly_active")
        assert unknown["tdee"] == lightly["tdee"]
        assert unknown["activity_multiplier"] == ACTIVITY_MULTIPLIERS["lightly_active"]
        assert unknown["activity_level"] == "lightly_active"

    def test_tdee_is_bmr_times_multiplier(self):
        result = calc_tdee(75, 175, 25, "male", "moderately_active")
        expected_tdee = result["bmr"] * ACTIVITY_MULTIPLIERS["moderately_active"]
        # Allow ±1 for rounding
        assert abs(result["tdee"] - round(expected_tdee)) <= 1

    def test_activity_level_normalised_in_output(self):
        result = calc_tdee(75, 175, 25, "male", "  Moderately_Active  ")
        assert result["activity_level"] == "moderately_active"

    def test_returns_integers_for_bmr_tdee(self):
        result = calc_tdee(75, 175, 25, "male", "lightly_active")
        assert isinstance(result["bmr"], int)
        assert isinstance(result["tdee"], int)


# ---------------------------------------------------------------------------
# calc_calorie_target
# ---------------------------------------------------------------------------

class TestCalcCalorieTarget:
    def test_lean_bulk_adds_surplus(self):
        result = calc_calorie_target(tdee=2500, goal="lean_bulk")
        assert result["target_kcal"] == 2500 + GOAL_ADJUSTMENTS_KCAL["lean_bulk"]

    def test_mini_cut_reduces_calories(self):
        result = calc_calorie_target(tdee=2500, goal="mini_cut")
        assert result["target_kcal"] == 2500 + GOAL_ADJUSTMENTS_KCAL["mini_cut"]

    def test_maintain_no_change(self):
        result = calc_calorie_target(tdee=2300, goal="maintain")
        assert result["target_kcal"] == 2300

    def test_deload_no_change(self):
        result = calc_calorie_target(tdee=2400, goal="deload")
        assert result["target_kcal"] == 2400

    def test_floor_clamping(self):
        # Very low TDEE should still be clamped up to floor
        result = calc_calorie_target(tdee=1000, goal="mini_cut")
        assert result["target_kcal"] == CALORIE_FLOOR_KCAL
        assert result["clamped"] is True

    def test_ceiling_clamping(self):
        # Very high TDEE with surplus should be clamped
        result = calc_calorie_target(tdee=6000, goal="lean_bulk")
        assert result["target_kcal"] == CALORIE_CEILING_KCAL
        assert result["clamped"] is True

    def test_no_clamping_for_normal_values(self):
        result = calc_calorie_target(tdee=2500, goal="lean_bulk")
        assert result["clamped"] is False

    def test_invalid_tdee_raises(self):
        with pytest.raises(ValueError, match="tdee must be > 0"):
            calc_calorie_target(0, "lean_bulk")
            
    def test_invalid_goal_raises(self):
        with pytest.raises(ValueError, match="Invalid goal: unknown"):
            calc_calorie_target(2500, "unknown")

    def test_normalises_goal_string(self):
        result = calc_calorie_target(2500, " Lean_Bulk ")
        assert result["goal"] == "lean_bulk"

    def test_returns_required_keys(self):
        result = calc_calorie_target(2500, "lean_bulk")
        for key in ("target_kcal", "adjustment_kcal", "tdee", "goal", "clamped"):
            assert key in result

    def test_adjustment_matches_goal(self):
        for goal, adj in GOAL_ADJUSTMENTS_KCAL.items():
            result = calc_calorie_target(2500, goal)
            assert result["adjustment_kcal"] == adj

    def test_floor_is_1400(self):
        assert CALORIE_FLOOR_KCAL == 1400

    def test_ceiling_is_6000(self):
        assert CALORIE_CEILING_KCAL == 6000
