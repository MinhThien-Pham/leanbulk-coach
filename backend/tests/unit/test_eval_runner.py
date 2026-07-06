from backend.evals.cases import EvalCase
from backend.evals.runner import run_eval_case, run_eval_suite

def test_run_eval_case_nutrition():
    case = EvalCase(
        id="nut_01",
        category="nutrition",
        description="valid lean bulk calorie/protein target",
        inputs={"weight_kg": 75.0, "height_cm": 180, "age": 25, "sex": "male", "goal": "lean_bulk", "activity_level": "moderately_active"},
        expected={"target_kcal_gt": 2000, "protein_g_gt": 120}
    )
    res = run_eval_case(case)
    assert res["passed"] is True
    assert res["score"] == 1.0

def test_run_eval_case_safety_failure():
    case = EvalCase(
        id="saf_01",
        category="safety",
        description="extreme calorie adjustment is flagged/blocked",
        inputs={"current_kcal": 2500, "proposed_kcal": 1500},
        expected={"error_contains": "exceeds the safe limit", "safe": False}
    )
    res = run_eval_case(case)
    assert res["passed"] is True

def test_run_eval_case_progress_insufficient():
    case = EvalCase(
        id="prog_01",
        category="progress",
        description="insufficient data",
        inputs={},
        expected={}
    )
    res = run_eval_case(case)
    assert res["passed"] is True
    assert res["observed"]["weight_trend"] == "insufficient_data"
    assert res["observed"]["sample_size"] == 1

def test_eval_case_result_format():
    case = EvalCase(
        id="nut_01",
        category="nutrition",
        description="format test",
        inputs={"weight_kg": 75.0, "height_cm": 180, "age": 25, "sex": "male", "goal": "lean_bulk", "activity_level": "moderately_active"},
        expected={"target_kcal_gt": 2000, "protein_g_gt": 120}
    )
    res = run_eval_case(case)
    assert "case_id" in res
    assert "category" in res
    assert "passed" in res
    assert "score" in res
    assert "details" in res
    assert "observed" in res

def test_run_eval_suite():
    res = run_eval_suite()
    assert res["total"] >= 12
    assert res["failed"] == 0
    assert res["score"] == 1.0
    assert len(res["results"]) == res["total"]
