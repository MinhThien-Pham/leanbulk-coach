from backend.agents.tool_registry import (
    get_all_tools, get_nutrition_tools, get_training_tools,
    get_progress_tools, get_safety_tools
)

def test_registry_contains_expected_tools():
    all_tools = get_all_tools()
    expected_names = [
        "calc_bmr", "calc_tdee", "calc_calorie_target", "calc_protein_target",
        "weight_trend", "check_rate_of_change", "suggest_linear_progression",
        "suggest_meals"
    ]
    for name in expected_names:
        assert name in all_tools
        assert callable(all_tools[name])

def test_subagent_tool_lists():
    assert len(get_nutrition_tools()) > 0
    assert len(get_training_tools()) > 0
    assert len(get_progress_tools()) > 0
    assert len(get_safety_tools()) > 0
