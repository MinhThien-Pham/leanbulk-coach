"""
test_progression_tools.py — Unit tests for backend/tools/progression_tools.py

Tests cover:
- suggest_linear_progression: increase, repeat, deload
- suggest_weekly_progression: batch exercise processing
- assess_strength_trend: consistent/moderate/inconsistent/stalled detection
"""

import pytest
from backend.tools.progression_tools import (
    DELOAD_LOAD_FACTOR,
    STALL_CONSECUTIVE_WEEKS,
    assess_strength_trend,
    suggest_linear_progression,
    suggest_weekly_progression,
)


# ---------------------------------------------------------------------------
# suggest_linear_progression
# ---------------------------------------------------------------------------

class TestSuggestLinearProgression:
    def test_returns_required_keys(self):
        result = suggest_linear_progression(60, target_reps=5, reps_achieved=5)
        for key in ("recommended_weight_kg", "recommended_reps", "progression_type",
                    "achieved_all_reps", "note"):
            assert key in result

    def test_all_reps_achieved_increases_weight(self):
        result = suggest_linear_progression(
            current_weight_kg=60, target_reps=5, reps_achieved=5, increment_kg=2.5
        )
        assert result["progression_type"] == "increase"
        assert result["recommended_weight_kg"] == 62.5
        assert result["achieved_all_reps"] is True

    def test_reps_not_achieved_stays_same_weight(self):
        result = suggest_linear_progression(
            current_weight_kg=60, target_reps=5, reps_achieved=4, increment_kg=2.5
        )
        assert result["progression_type"] == "repeat"
        assert result["recommended_weight_kg"] == 60.0
        assert result["achieved_all_reps"] is False

    def test_deload_mode_halves_weight(self):
        result = suggest_linear_progression(
            current_weight_kg=100, target_reps=5, reps_achieved=5, deload_mode=True
        )
        assert result["progression_type"] == "deload"
        assert result["recommended_weight_kg"] == pytest.approx(100 * DELOAD_LOAD_FACTOR)

    def test_deload_load_factor_is_half(self):
        assert DELOAD_LOAD_FACTOR == 0.5

    def test_deload_mode_overrides_reps_achieved(self):
        # Even if reps achieved, deload_mode should return deload
        result = suggest_linear_progression(
            current_weight_kg=80, target_reps=5, reps_achieved=0, deload_mode=True
        )
        assert result["progression_type"] == "deload"

    def test_note_is_non_empty_string(self):
        result = suggest_linear_progression(60, 5, 5)
        assert isinstance(result["note"], str)
        assert len(result["note"]) > 0

    def test_custom_increment_applied(self):
        result = suggest_linear_progression(60, target_reps=5, reps_achieved=5, increment_kg=5.0)
        assert result["recommended_weight_kg"] == 65.0

    def test_reps_exceeding_target_also_increases(self):
        # More reps than target = also increase weight
        result = suggest_linear_progression(60, target_reps=5, reps_achieved=8)
        assert result["progression_type"] == "increase"

    def test_deload_weight_rounded_to_2dp(self):
        result = suggest_linear_progression(75, 5, 5, deload_mode=True)
        expected = round(75 * DELOAD_LOAD_FACTOR, 2)
        assert result["recommended_weight_kg"] == expected

    def test_zero_weight_deload(self):
        result = suggest_linear_progression(0, 5, 5, deload_mode=True)
        assert result["recommended_weight_kg"] == 0.0


# ---------------------------------------------------------------------------
# suggest_weekly_progression
# ---------------------------------------------------------------------------

class TestSuggestWeeklyProgression:
    def _exercise(self, name, weight, target, achieved, increment=2.5):
        return {
            "name": name,
            "current_weight_kg": weight,
            "target_reps": target,
            "reps_achieved": achieved,
            "increment_kg": increment,
        }

    def test_returns_list(self):
        exercises = [self._exercise("Squat", 60, 5, 5)]
        result = suggest_weekly_progression(exercises)
        assert isinstance(result, list)

    def test_each_result_has_exercise_name(self):
        exercises = [self._exercise("Bench Press", 50, 5, 5)]
        result = suggest_weekly_progression(exercises)
        assert result[0]["exercise"] == "Bench Press"

    def test_multiple_exercises_processed(self):
        exercises = [
            self._exercise("Squat", 60, 5, 5),
            self._exercise("Bench Press", 50, 5, 4),
            self._exercise("Deadlift", 80, 5, 5),
        ]
        result = suggest_weekly_progression(exercises)
        assert len(result) == 3

    def test_deload_mode_applies_to_all(self):
        exercises = [
            self._exercise("Squat", 60, 5, 5),
            self._exercise("Bench", 50, 5, 5),
        ]
        result = suggest_weekly_progression(exercises, deload_mode=True)
        assert all(r["progression_type"] == "deload" for r in result)

    def test_empty_list_returns_empty(self):
        result = suggest_weekly_progression([])
        assert result == []

    def test_correct_progression_per_exercise(self):
        exercises = [
            self._exercise("Squat", 60, 5, 5),    # Should increase
            self._exercise("Bench", 50, 5, 4),     # Should repeat
        ]
        result = suggest_weekly_progression(exercises)
        squat = next(r for r in result if r["exercise"] == "Squat")
        bench = next(r for r in result if r["exercise"] == "Bench")
        assert squat["progression_type"] == "increase"
        assert bench["progression_type"] == "repeat"

    def test_missing_increment_uses_default(self):
        exercises = [{"name": "Squat", "current_weight_kg": 60, "target_reps": 5, "reps_achieved": 5}]
        result = suggest_weekly_progression(exercises)
        # Should not raise; uses default increment of 2.5
        assert result[0]["recommended_weight_kg"] == 62.5


# ---------------------------------------------------------------------------
# assess_strength_trend
# ---------------------------------------------------------------------------

class TestAssessStrengthTrend:
    def test_returns_required_keys(self):
        result = assess_strength_trend([3, 3, 3], weekly_planned=3)
        for key in ("trend", "avg_completion_pct", "completion_pcts", "stalled"):
            assert key in result

    def test_consistent_trend(self):
        result = assess_strength_trend([3, 3, 3, 3], weekly_planned=3)
        assert result["trend"] == "consistent"
        assert result["avg_completion_pct"] == 100.0

    def test_moderate_trend(self):
        result = assess_strength_trend([2, 2, 2, 2], weekly_planned=3)
        # 2/3 = 66.7%
        assert result["trend"] == "inconsistent"  # below 70%

    def test_very_inconsistent_trend(self):
        result = assess_strength_trend([1, 0, 1, 0], weekly_planned=3)
        assert result["trend"] == "very_inconsistent"

    def test_stall_detection(self):
        # Last 2 weeks (STALL_CONSECUTIVE_WEEKS) all below 70%
        result = assess_strength_trend([3, 1, 1], weekly_planned=3)
        assert result["stalled"] is True

    def test_no_stall_when_recent_improvement(self):
        result = assess_strength_trend([1, 1, 3], weekly_planned=3)
        assert result["stalled"] is False

    def test_insufficient_data_empty_list(self):
        result = assess_strength_trend([], weekly_planned=3)
        assert result["trend"] == "insufficient_data"
        assert result["avg_completion_pct"] is None

    def test_zero_planned_returns_insufficient(self):
        result = assess_strength_trend([3, 3], weekly_planned=0)
        assert result["trend"] == "insufficient_data"

    def test_completion_pcts_length_matches_input(self):
        result = assess_strength_trend([3, 2, 3], weekly_planned=3)
        assert len(result["completion_pcts"]) == 3

    def test_stall_consecutive_weeks_is_2(self):
        assert STALL_CONSECUTIVE_WEEKS == 2

    def test_avg_completion_pct_is_rounded(self):
        result = assess_strength_trend([2, 2], weekly_planned=3)
        # 2/3 * 100 = 66.666... rounded to 1dp
        assert result["avg_completion_pct"] == pytest.approx(66.7, abs=0.1)
