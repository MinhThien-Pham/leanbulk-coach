"""
test_protein_tools.py — Unit tests for backend/tools/protein_tools.py

Tests cover:
- Protein targets for all goals
- kg to lb conversion accuracy
- Floor and ceiling bounds
- protein_from_food_sources equivalencies
"""

import pytest
from backend.tools.protein_tools import (
    KG_TO_LB,
    PROTEIN_CEILING_G,
    PROTEIN_FLOOR_G,
    PROTEIN_RATES_G_PER_LB,
    calc_protein_target,
    protein_from_food_sources,
)


class TestCalcProteinTarget:
    def test_returns_required_keys(self):
        result = calc_protein_target(70, "lean_bulk")
        for key in ("protein_g", "protein_per_lb", "protein_per_kg", "weight_lb", "weight_kg", "goal", "clamped"):
            assert key in result

    def test_lean_bulk_rate(self):
        result = calc_protein_target(70, "lean_bulk")
        assert result["protein_per_lb"] == PROTEIN_RATES_G_PER_LB["lean_bulk"]

    def test_mini_cut_rate_higher_than_lean_bulk(self):
        # Mini-cut should have a higher rate to protect muscle
        lean_bulk_rate = PROTEIN_RATES_G_PER_LB["lean_bulk"]
        mini_cut_rate = PROTEIN_RATES_G_PER_LB["mini_cut"]
        assert mini_cut_rate > lean_bulk_rate

    def test_all_goals_return_valid_target(self):
        for goal in PROTEIN_RATES_G_PER_LB:
            result = calc_protein_target(75, goal)
            assert result["protein_g"] >= PROTEIN_FLOOR_G
            assert result["protein_g"] <= PROTEIN_CEILING_G

    def test_weight_lb_conversion(self):
        weight_kg = 70.0
        result = calc_protein_target(weight_kg, "lean_bulk")
        expected_lb = round(weight_kg * KG_TO_LB, 1)
        assert result["weight_lb"] == expected_lb

    def test_protein_per_kg_is_derived_from_per_lb(self):
        result = calc_protein_target(70, "lean_bulk")
        expected_per_kg = round(result["protein_per_lb"] * KG_TO_LB, 2)
        assert result["protein_per_kg"] == expected_per_kg

    def test_floor_clamping(self):
        # Very light person (35 kg) might hit floor
        result = calc_protein_target(35, "deload")
        assert result["protein_g"] >= PROTEIN_FLOOR_G

    def test_no_clamping_for_normal_weight(self):
        result = calc_protein_target(75, "lean_bulk")
        assert result["clamped"] is False

    def test_heavier_person_gets_more_protein(self):
        light = calc_protein_target(60, "lean_bulk")
        heavy = calc_protein_target(100, "lean_bulk")
        assert heavy["protein_g"] > light["protein_g"]

    def test_invalid_weight_raises(self):
        with pytest.raises(ValueError, match="weight_kg must be > 0"):
            calc_protein_target(0, "lean_bulk")

    def test_invalid_goal_raises(self):
        with pytest.raises(ValueError, match="Invalid goal: unknown"):
            calc_protein_target(75, "unknown")

    def test_normalises_goal_string(self):
        result = calc_protein_target(75, " Lean_Bulk ")
        assert result["goal"] == "lean_bulk"

    def test_result_is_integer(self):
        result = calc_protein_target(75, "lean_bulk")
        assert isinstance(result["protein_g"], int)

    def test_floor_is_100(self):
        assert PROTEIN_FLOOR_G == 100

    def test_ceiling_is_350(self):
        assert PROTEIN_CEILING_G == 350

    def test_lean_bulk_rate_is_0_82(self):
        assert PROTEIN_RATES_G_PER_LB["lean_bulk"] == pytest.approx(0.82)


class TestProteinFromFoodSources:
    def test_returns_required_keys(self):
        result = protein_from_food_sources(150, 70)
        for key in ("protein_g", "chicken_breast_g", "eggs_approx", "greek_yogurt_g"):
            assert key in result

    def test_protein_g_matches_input(self):
        result = protein_from_food_sources(150, 70)
        assert result["protein_g"] == 150

    def test_chicken_breast_positive(self):
        result = protein_from_food_sources(150, 70)
        assert result["chicken_breast_g"] > 0

    def test_eggs_approx_reasonable(self):
        # 150g protein / 6g per egg = 25 eggs
        result = protein_from_food_sources(150, 70)
        assert result["eggs_approx"] == 25

    def test_higher_protein_more_food(self):
        low = protein_from_food_sources(100, 70)
        high = protein_from_food_sources(200, 70)
        assert high["chicken_breast_g"] > low["chicken_breast_g"]
        assert high["eggs_approx"] > low["eggs_approx"]
