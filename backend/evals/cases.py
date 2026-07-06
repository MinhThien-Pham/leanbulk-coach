from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class EvalCase:
    id: str
    category: str
    description: str
    inputs: Dict[str, Any]
    expected: Dict[str, Any]

def get_default_eval_cases() -> list[EvalCase]:
    return [
        EvalCase(
            id="nut_01",
            category="nutrition",
            description="valid lean bulk calorie/protein target",
            inputs={"weight_kg": 75.0, "height_cm": 180, "age": 25, "sex": "male", "goal": "lean_bulk", "activity_level": "moderately_active"},
            expected={"target_kcal_gt": 2000, "protein_g_gt": 120}
        ),
        EvalCase(
            id="nut_02",
            category="nutrition",
            description="invalid negative bodyweight should fail safely",
            inputs={"weight_kg": -10.0, "height_cm": 180, "age": 25, "sex": "male", "goal": "lean_bulk", "activity_level": "lightly_active"},
            expected={"error_contains": "must be > 0"}
        ),
        EvalCase(
            id="nut_03",
            category="nutrition",
            description="vegetarian meal suggestion should exclude meat meals",
            inputs={"target_kcal": 600, "dietary_preferences": ["vegetarian"]},
            expected={"exclude_words": ["pork", "beef", "chicken", "meat"]}
        ),
        EvalCase(
            id="trn_01",
            category="training",
            description="linear progression success increases weight",
            inputs={"current_weight_kg": 100.0, "reps_completed": 10, "target_reps": 8},
            expected={"next_weight_kg_gt": 100.0}
        ),
        EvalCase(
            id="trn_02",
            category="training",
            description="failed reps repeats weight",
            inputs={"current_weight_kg": 100.0, "reps_completed": 6, "target_reps": 8, "consecutive_failures": 1},
            expected={"next_weight_kg": 100.0}
        ),
        EvalCase(
            id="trn_03",
            category="training",
            description="deload mode reduces weight safely",
            inputs={"current_weight_kg": 100.0, "reps_completed": 5, "target_reps": 8, "consecutive_failures": 3},
            expected={"next_weight_kg_lt": 100.0}
        ),
        EvalCase(
            id="prog_01",
            category="progress",
            description="insufficient trend data returns insufficient_data",
            inputs={"logs_count": 1},
            expected={"trend": "insufficient_data"}
        ),
        EvalCase(
            id="prog_02",
            category="progress",
            description="gaining trend with stable waist is acceptable",
            inputs={"curr_weight": 80.0, "prev_weight": 79.5, "curr_waist": 80.0, "prev_waist": 80.0},
            expected={"weight_trend": "gaining", "waist_trend": "stable"}
        ),
        EvalCase(
            id="saf_01",
            category="safety",
            description="extreme calorie adjustment is flagged/blocked",
            inputs={"current_kcal": 2500, "proposed_kcal": 1500},
            expected={"error_contains": "exceeds the safe limit", "safe": False}
        ),
        EvalCase(
            id="saf_02",
            category="safety",
            description="pain phrase triggers safety warning/refusal flag",
            inputs={"user_message": "my lower back hurts a lot during deadlifts"},
            expected={"pain_flagged": True}
        ),
        EvalCase(
            id="wf_01",
            category="workflow",
            description="local demo flow returns live_llm_calls False",
            inputs={},
            expected={"live_llm_calls": False, "summary_status": "mocked_or_string"}
        ),
        EvalCase(
            id="api_01",
            category="api",
            description="FastAPI /health and /tools/calorie-target deterministic smoke test",
            inputs={"weight_kg": 75.0, "height_cm": 180, "age": 25, "sex": "male", "goal": "lean_bulk", "activity_level": "lightly_active"},
            expected={"health_status": 200, "calorie_status": 200}
        )
    ]
