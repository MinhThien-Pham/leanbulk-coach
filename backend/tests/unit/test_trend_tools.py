"""
test_trend_tools.py — Unit tests for backend/tools/trend_tools.py

Tests cover:
- 7-day average calculation (nulls, zeros, partial data)
- Weight trend classification (all 5 trend types)
- Waist trend classification (all 6 trend types including baseline)
- Adherence score calculation and flag generation
- Edge cases (zeros, empty lists, equal values)
"""

import pytest
from backend.tools.trend_tools import (
    LOW_ADHERENCE_PCT,
    WEIGHT_GAINING_FAST_KG,
    adherence_score,
    calc_7day_average,
    waist_trend,
    weight_trend,
)
from backend.tools.safety_tools import WAIST_CREEP_THRESHOLD_CM


# ---------------------------------------------------------------------------
# calc_7day_average
# ---------------------------------------------------------------------------

class TestCalc7DayAverage:
    def test_basic_average(self):
        result = calc_7day_average([70, 71, 70, 72, 70, 71, 70])
        assert result == pytest.approx(70.57, abs=0.01)

    def test_filters_none_values(self):
        result = calc_7day_average([70, None, 71, None, 70])
        # Average of [70, 71, 70] = 70.33
        assert result == pytest.approx(70.33, abs=0.01)

    def test_filters_zero_values(self):
        result = calc_7day_average([0, 70, 71, 0, 70])
        assert result == pytest.approx(70.33, abs=0.01)

    def test_all_none_returns_none(self):
        assert calc_7day_average([None, None, None]) is None

    def test_empty_list_returns_none(self):
        assert calc_7day_average([]) is None

    def test_single_value(self):
        assert calc_7day_average([72.5]) == 72.5

    def test_result_rounded_to_2dp(self):
        result = calc_7day_average([70.1, 70.2, 70.3])
        # 70.1+70.2+70.3 = 210.6 / 3 = 70.2
        assert result == 70.2


# ---------------------------------------------------------------------------
# weight_trend
# ---------------------------------------------------------------------------

class TestWeightTrend:
    def _week(self, avg_kg: float) -> list[float]:
        """Helper: create a uniform 7-day list."""
        return [avg_kg] * 7

    def test_returns_required_keys(self):
        result = weight_trend(self._week(72), self._week(71.5))
        for key in ("current_avg_kg", "previous_avg_kg", "delta_kg", "delta_lb", "trend", "error"):
            assert key in result

    def test_stable_trend(self):
        result = weight_trend(self._week(72.0), self._week(72.0))
        assert result["trend"] == "stable"
        assert result["delta_kg"] == 0.0

    def test_gaining_trend(self):
        result = weight_trend(self._week(72.3), self._week(72.0))
        assert result["trend"] == "gaining"

    def test_gaining_fast_trend(self):
        result = weight_trend(self._week(72.6), self._week(72.0))
        assert result["trend"] == "gaining_fast"

    def test_losing_trend(self):
        result = weight_trend(self._week(71.8), self._week(72.0))
        assert result["trend"] == "losing"

    def test_losing_fast_trend(self):
        result = weight_trend(self._week(71.4), self._week(72.0))
        assert result["trend"] == "losing_fast"

    def test_gaining_fast_threshold(self):
        # Exactly at threshold should be gaining_fast
        result = weight_trend(self._week(72.0 + WEIGHT_GAINING_FAST_KG + 0.01), self._week(72.0))
        assert result["trend"] == "gaining_fast"

    def test_no_previous_data_returns_insufficient(self):
        result = weight_trend(self._week(72.0), [])
        assert result["trend"] == "insufficient_data"
        assert result["previous_avg_kg"] is None

    def test_no_current_data_returns_error(self):
        result = weight_trend([], self._week(72.0))
        assert result["error"] is not None
        assert result["trend"] == "insufficient_data"
        assert result["current_avg_kg"] is None

    def test_delta_lb_conversion(self):
        # +0.5 kg should be ~+1.1 lb
        result = weight_trend(self._week(72.5), self._week(72.0))
        assert result["delta_lb"] == pytest.approx(0.5 * 2.20462, abs=0.01)

    def test_positive_delta_is_gain(self):
        result = weight_trend(self._week(73.0), self._week(72.0))
        assert result["delta_kg"] > 0

    def test_negative_delta_is_loss(self):
        result = weight_trend(self._week(71.0), self._week(72.0))
        assert result["delta_kg"] < 0

    def test_mixed_week_with_nulls(self):
        current = [72.0, 72.2, None, 72.1, 72.3, None, 72.0]
        previous = [71.5] * 7
        result = weight_trend(current, previous)
        assert result["current_avg_kg"] is not None
        assert result["trend"] in ("gaining", "gaining_fast", "stable")


# ---------------------------------------------------------------------------
# waist_trend
# ---------------------------------------------------------------------------

class TestWaistTrend:
    def test_returns_required_keys(self):
        result = waist_trend(85.0, 84.5)
        for key in ("current_cm", "previous_cm", "delta_cm", "trend"):
            assert key in result

    def test_baseline_when_no_previous(self):
        result = waist_trend(85.0, None)
        assert result["trend"] == "baseline"
        assert result["delta_cm"] is None
        assert result["previous_cm"] is None

    def test_stable_waist(self):
        result = waist_trend(85.0, 85.0)
        assert result["trend"] == "stable"
        assert result["delta_cm"] == 0.0

    def test_increasing_fast(self):
        result = waist_trend(86.0, 85.0)  # +1.0 cm
        assert result["trend"] == "increasing_fast"

    def test_increasing(self):
        result = waist_trend(85.4, 85.0)  # +0.4 cm
        assert result["trend"] == "increasing"

    def test_decreasing(self):
        result = waist_trend(84.6, 85.0)  # -0.4 cm
        assert result["trend"] == "decreasing"

    def test_decreasing_fast(self):
        result = waist_trend(84.0, 85.0)  # -1.0 cm
        assert result["trend"] == "decreasing_fast"

    def test_waist_creep_threshold(self):
        # Just over threshold should be increasing_fast
        result = waist_trend(85.0 + WAIST_CREEP_THRESHOLD_CM + 0.1, 85.0)
        assert result["trend"] == "increasing_fast"

    def test_delta_rounded_to_1dp(self):
        result = waist_trend(85.35, 85.0)
        assert result["delta_cm"] == round(0.35, 1)


# ---------------------------------------------------------------------------
# adherence_score
# ---------------------------------------------------------------------------

class TestAdherenceScore:
    def test_returns_required_keys(self):
        result = adherence_score(2500, 2500, 160, 160, 3, 3)
        for key in ("calorie_pct", "protein_pct", "workout_pct", "overall_pct", "flags", "is_low"):
            assert key in result

    def test_perfect_adherence(self):
        result = adherence_score(2500, 2500, 160, 160, 3, 3)
        assert result["calorie_pct"] == 100.0
        assert result["protein_pct"] == 100.0
        assert result["workout_pct"] == 100.0
        assert result["overall_pct"] == 100.0
        assert result["flags"] == []
        assert result["is_low"] is False

    def test_zero_adherence(self):
        result = adherence_score(0, 2500, 0, 160, 0, 3)
        assert result["calorie_pct"] == 0.0
        assert result["protein_pct"] == 0.0
        assert result["workout_pct"] == 0.0
        assert result["is_low"] is True

    def test_low_calorie_flag(self):
        result = adherence_score(1500, 2500, 160, 160, 3, 3)
        assert "low_calorie_adherence" in result["flags"]

    def test_low_protein_flag(self):
        result = adherence_score(2500, 2500, 100, 160, 3, 3)
        assert "low_protein_adherence" in result["flags"]

    def test_low_workout_flag(self):
        result = adherence_score(2500, 2500, 160, 160, 1, 3)
        assert "low_workout_adherence" in result["flags"]

    def test_all_flags_when_all_low(self):
        result = adherence_score(1000, 2500, 80, 160, 1, 3)
        assert "low_calorie_adherence" in result["flags"]
        assert "low_protein_adherence" in result["flags"]
        assert "low_workout_adherence" in result["flags"]

    def test_no_flags_for_borderline_high(self):
        # 70% is the threshold — 71% should pass
        result = adherence_score(
            actual_calories=2500 * 0.71,
            target_calories=2500,
            actual_protein_g=160 * 0.71,
            target_protein_g=160,
            workouts_completed=2,
            workouts_planned=3,  # 66.7% — will flag workout
        )
        assert "low_calorie_adherence" not in result["flags"]
        assert "low_protein_adherence" not in result["flags"]

    def test_is_low_threshold(self):
        assert LOW_ADHERENCE_PCT == 70.0

    def test_overall_is_average_of_three(self):
        result = adherence_score(2500, 2500, 160, 160, 2, 3)
        # cal=100, protein=100, workout=66.7
        expected_overall = round((100.0 + 100.0 + 66.7) / 3, 1)
        assert result["overall_pct"] == expected_overall

    def test_zero_target_calories_returns_zero_pct(self):
        result = adherence_score(0, 0, 160, 160, 3, 3)
        assert result["calorie_pct"] == 0.0

    def test_zero_target_workouts_returns_zero_pct(self):
        result = adherence_score(2500, 2500, 160, 160, 0, 0)
        assert result["workout_pct"] == 0.0
