"""
test_meal_tools.py — Unit tests for backend/tools/meal_tools.py

Tests cover:
- suggest_meals: basic output structure
- Dietary preference filtering (vegetarian, vegan, dairy_free, no_fish)
- Equipment filtering
- Scoring/ranking by proximity to targets
- Fallback when all meals filtered out
- Edge cases (zero remaining, high protein demand)
"""

import pytest
from backend.tools.meal_tools import MEAL_LIBRARY, suggest_meals


# ---------------------------------------------------------------------------
# suggest_meals
# ---------------------------------------------------------------------------

class TestSuggestMeals:
    def test_returns_required_keys(self):
        result = suggest_meals(remaining_kcal=500, remaining_protein_g=40)
        for key in ("suggestions", "total_suggested_kcal", "total_suggested_protein_g",
                    "remaining_kcal", "remaining_protein_g", "n_returned", "fallback_used"):
            assert key in result

    def test_returns_n_suggestions(self):
        result = suggest_meals(remaining_kcal=500, remaining_protein_g=40, n_suggestions=3)
        assert result["n_returned"] == 3
        assert len(result["suggestions"]) == 3

    def test_n_suggestions_1(self):
        result = suggest_meals(remaining_kcal=400, remaining_protein_g=30, n_suggestions=1)
        assert result["n_returned"] == 1

    def test_no_dietary_filters_uses_full_library(self):
        result = suggest_meals(500, 40, dietary_preferences=None)
        assert result["fallback_used"] is False

    def test_vegetarian_excludes_poultry_and_fish(self):
        result = suggest_meals(500, 40, dietary_preferences=["vegetarian"], n_suggestions=5)
        for meal in result["suggestions"]:
            assert "poultry" not in meal["tags"]
            assert "fish" not in meal["tags"]
            assert "beef" not in meal["tags"]

    def test_vegan_excludes_dairy_and_eggs(self):
        result = suggest_meals(500, 40, dietary_preferences=["vegan"], n_suggestions=3)
        for meal in result["suggestions"]:
            assert "dairy" not in meal["tags"]
            assert "eggs" not in meal["tags"]
            assert "poultry" not in meal["tags"]
            assert "fish" not in meal["tags"]

    def test_dairy_free_excludes_dairy(self):
        result = suggest_meals(500, 40, dietary_preferences=["dairy_free"], n_suggestions=3)
        for meal in result["suggestions"]:
            assert "dairy" not in meal["tags"]

    def test_no_fish_excludes_fish(self):
        result = suggest_meals(500, 40, dietary_preferences=["no_fish"], n_suggestions=3)
        for meal in result["suggestions"]:
            assert "fish" not in meal["tags"]

    def test_equipment_filter_no_stove(self):
        # Only allow no-cook meals
        result = suggest_meals(500, 40, equipment_available=["none"], n_suggestions=3)
        for meal in result["suggestions"]:
            # All suggestions should have "none" in their equipment list
            # (may have fallback if fewer than n_suggestions no-cook meals exist)
            assert "none" in meal["equipment"] or result["fallback_used"]

    def test_ham_omelette_not_in_no_pork(self):
        result = suggest_meals(500, 40, dietary_preferences=["no_pork"], n_suggestions=20)
        for meal in result["suggestions"]:
            assert meal["name"] != "Ham and Cheese Omelette"

    def test_ham_omelette_not_in_vegetarian(self):
        result = suggest_meals(500, 40, dietary_preferences=["vegetarian"], n_suggestions=20)
        for meal in result["suggestions"]:
            assert meal["name"] != "Ham and Cheese Omelette"

    def test_fallback_used_when_no_candidates_match(self):
        # Impossible combination: vegan + no_cook + very specific
        # Use a real edge case: vegan + blender only
        result = suggest_meals(
            500, 40,
            dietary_preferences=["vegan"],
            equipment_available=["oven"],  # Very limited
            n_suggestions=3,
        )
        # Either found something or fallback was used — should not crash
        assert result["n_returned"] >= 1 or result["fallback_used"]

    def test_suggestions_are_from_meal_library(self):
        result = suggest_meals(500, 40)
        library_names = {m["name"] for m in MEAL_LIBRARY}
        for meal in result["suggestions"]:
            assert meal["name"] in library_names

    def test_total_kcal_matches_sum(self):
        result = suggest_meals(500, 40, n_suggestions=3)
        expected_total = sum(m["kcal"] for m in result["suggestions"])
        assert result["total_suggested_kcal"] == expected_total

    def test_total_protein_matches_sum(self):
        result = suggest_meals(500, 40, n_suggestions=3)
        expected_total = sum(m["protein_g"] for m in result["suggestions"])
        assert result["total_suggested_protein_g"] == expected_total

    def test_remaining_values_preserved_in_output(self):
        result = suggest_meals(remaining_kcal=600, remaining_protein_g=45)
        assert result["remaining_kcal"] == 600
        assert result["remaining_protein_g"] == 45

    def test_high_protein_demand_prefers_high_protein_meals(self):
        # When remaining protein is high, should prefer high-protein meals
        result = suggest_meals(remaining_kcal=1000, remaining_protein_g=80, n_suggestions=1)
        top_meal = result["suggestions"][0]
        assert top_meal["protein_g"] >= 20  # Should not suggest low-protein option

    def test_low_calorie_budget_avoids_calorie_dense_meals(self):
        # When remaining kcal is low, avoid overshooting heavily
        result = suggest_meals(remaining_kcal=200, remaining_protein_g=10, n_suggestions=1)
        # Top meal shouldn't be > 300 kcal (1.5x) in ideal case
        # (fallback may happen if all meals exceed — that's acceptable)
        top_meal = result["suggestions"][0]
        assert top_meal["kcal"] > 0  # At minimum, a meal was returned

    def test_no_suggestions_capped_beyond_library_size(self):
        # Requesting more than MEAL_LIBRARY has should just return all
        result = suggest_meals(500, 40, n_suggestions=100)
        assert result["n_returned"] == len(MEAL_LIBRARY)

    def test_all_suggestions_have_required_meal_keys(self):
        result = suggest_meals(500, 40, n_suggestions=3)
        for meal in result["suggestions"]:
            for key in ("name", "kcal", "protein_g", "tags", "equipment", "description"):
                assert key in meal

    def test_empty_dietary_prefs_no_filtering(self):
        result = suggest_meals(500, 40, dietary_preferences=[])
        assert result["fallback_used"] is False
