from backend.evals.reporting import format_eval_report

def test_format_eval_report():
    suite_result = {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "score": 0.5,
        "results": [
            {"case_id": "c1", "category": "nutrition", "passed": True},
            {"case_id": "c2", "category": "safety", "passed": False}
        ]
    }
    rep = format_eval_report(suite_result)
    assert "Total Cases: 2" in rep
    assert "Passed:      1" in rep
    assert "Failed:      1" in rep
    assert "Score:       50.0%" in rep
    assert "nutrition: 1 passed, 0 failed" in rep
    assert "safety: 0 passed, 1 failed" in rep
    assert "Failed Case IDs:" in rep
    assert "- c2 (safety)" in rep
