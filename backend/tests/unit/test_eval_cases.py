from backend.evals.cases import get_default_eval_cases

def test_eval_cases_default():
    cases = get_default_eval_cases()
    assert len(cases) >= 12
    
    categories = {c.category for c in cases}
    expected_categories = {"nutrition", "training", "progress", "safety", "workflow", "api"}
    assert categories == expected_categories
    
    ids = [c.id for c in cases]
    assert len(ids) == len(set(ids))
