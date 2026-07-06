from backend.evals.cases import EvalCase, get_default_eval_cases
from backend.tools.calorie_tools import calc_tdee, calc_calorie_target
from backend.tools.protein_tools import calc_protein_target
from backend.tools.meal_tools import suggest_meals
from backend.tools.progression_tools import suggest_linear_progression
from backend.tools.trend_tools import weight_trend, waist_trend
from backend.tools.safety_tools import check_calorie_adjustment, check_pain_flag
from backend.workflows.demo_flow import run_local_demo_flow
import asyncio
from backend.app.main import create_app
from fastapi.testclient import TestClient
from backend.db.session import create_sqlite_async_engine, create_async_session_factory, init_db
from backend.db.repositories import create_user_profile, add_body_metric_log
from backend.mcp_server.context_tools import get_progress_summary_context

async def _run_insufficient_progress_eval() -> dict:
    engine = create_sqlite_async_engine("sqlite+aiosqlite:///:memory:")
    await init_db(engine)
    factory = create_async_session_factory(engine)
    try:
        async with factory() as session:
            user = await create_user_profile(session, display_name="Test User", sex="male", age=30, height_cm=180.0, goal="lean_bulk", target_weight_kg=80.0)
            await add_body_metric_log(session, user_id=user.id, weight_kg=75.0, waist_cm=80.0)
            return await get_progress_summary_context(session, user.id)
    finally:
        await engine.dispose()

def run_nutrition_case(case: EvalCase) -> tuple[dict, bool]:
    obs = {}
    passed = False
    try:
        if case.id == "nut_01":
            tdee_res = calc_tdee(case.inputs["weight_kg"], case.inputs["height_cm"], case.inputs["age"], case.inputs["sex"], case.inputs["activity_level"])
            tgt = calc_calorie_target(tdee_res["tdee"], case.inputs["goal"])["target_kcal"]
            pro = calc_protein_target(case.inputs["weight_kg"], case.inputs["goal"])["protein_g"]
            obs["target_kcal"] = tgt
            obs["protein_g"] = pro
            passed = tgt > case.expected["target_kcal_gt"] and pro > case.expected["protein_g_gt"]
        elif case.id == "nut_02":
            try:
                calc_tdee(case.inputs["weight_kg"], case.inputs["height_cm"], case.inputs["age"], case.inputs["sex"], case.inputs["activity_level"])
                passed = False
            except ValueError as e:
                obs["error"] = str(e)
                passed = case.expected["error_contains"] in str(e)
        elif case.id == "nut_03":
            meals = suggest_meals(
                remaining_kcal=case.inputs["target_kcal"],
                remaining_protein_g=50,
                dietary_preferences=case.inputs["dietary_preferences"]
            )
            words = str(meals).lower()
            obs["words"] = words
            passed = all(w not in words for w in case.expected["exclude_words"])
    except Exception as e:
        obs["exception"] = str(e)
    return obs, passed

def run_training_case(case: EvalCase) -> tuple[dict, bool]:
    obs = {}
    passed = False
    try:
        deload = False
        if case.inputs.get("consecutive_failures", 0) >= 3:
            deload = True
        res = suggest_linear_progression(
            current_weight_kg=case.inputs["current_weight_kg"],
            target_reps=case.inputs["target_reps"],
            reps_achieved=case.inputs["reps_completed"],
            deload_mode=deload
        )
        obs["next_weight_kg"] = res["recommended_weight_kg"]
        if case.id == "trn_01":
            passed = res["recommended_weight_kg"] > case.expected["next_weight_kg_gt"]
        elif case.id == "trn_02":
            passed = res["recommended_weight_kg"] == case.expected["next_weight_kg"]
        elif case.id == "trn_03":
            passed = res["recommended_weight_kg"] < case.expected["next_weight_kg_lt"]
    except Exception as e:
        obs["exception"] = str(e)
    return obs, passed

def run_progress_case(case: EvalCase) -> tuple[dict, bool]:
    obs = {}
    passed = False
    try:
        if case.id == "prog_01":
            res = asyncio.run(_run_insufficient_progress_eval())
            obs["weight_trend"] = res.get("weight_trend")
            obs["waist_trend"] = res.get("waist_trend")
            obs["sample_size"] = res.get("sample_size")
            passed = obs["weight_trend"] == "insufficient_data" and obs["waist_trend"] == "insufficient_data"
        elif case.id == "prog_02":
            w_trend = weight_trend([case.inputs["curr_weight"]], [case.inputs["prev_weight"]])
            wa_trend = waist_trend(case.inputs["curr_waist"], case.inputs["prev_waist"])
            obs["weight_trend"] = w_trend["trend"]
            obs["waist_trend"] = wa_trend["trend"]
            passed = w_trend["trend"] == case.expected["weight_trend"] and wa_trend["trend"] == case.expected["waist_trend"]
    except Exception as e:
        obs["exception"] = str(e)
    return obs, passed

def run_safety_case(case: EvalCase) -> tuple[dict, bool]:
    obs = {}
    passed = False
    try:
        if case.id == "saf_01":
            adj = case.inputs["proposed_kcal"] - case.inputs["current_kcal"]
            res = check_calorie_adjustment(adj, "mini_cut")
            obs["safe"] = res["is_safe"]
            obs["warnings"] = res["warnings"]
            passed = any(case.expected["error_contains"] in w for w in res["warnings"]) and res["is_safe"] == case.expected["safe"]
        elif case.id == "saf_02":
            flag_result = check_pain_flag(case.inputs["user_message"])
            obs["pain_flagged"] = flag_result["pain_detected"]
            passed = flag_result["pain_detected"] == case.expected["pain_flagged"]
    except Exception as e:
        obs["exception"] = str(e)
    return obs, passed

def run_workflow_case(case: EvalCase) -> tuple[dict, bool]:
    obs = {}
    passed = False
    try:
        if case.id == "wf_01":
            res = asyncio.run(run_local_demo_flow())
            obs["live_llm_calls"] = res["metadata"]["live_llm_calls"]
            obs["summary_status"] = type(res["summary"]).__name__
            passed = obs["live_llm_calls"] is False
    except Exception as e:
        obs["exception"] = str(e)
    return obs, passed

def run_api_case(case: EvalCase) -> tuple[dict, bool]:
    obs = {}
    passed = False
    try:
        if case.id == "api_01":
            app = create_app(init_db_on_startup=False)
            with TestClient(app) as client:
                h = client.get("/health")
                t = client.post("/tools/calorie-target", json=case.inputs)
                obs["health_status"] = h.status_code
                obs["calorie_status"] = t.status_code
                passed = h.status_code == case.expected["health_status"] and t.status_code == case.expected["calorie_status"]
    except Exception as e:
        obs["exception"] = str(e)
    return obs, passed

def run_eval_case(case: EvalCase) -> dict:
    obs = {}
    passed = False
    
    if case.category == "nutrition":
        obs, passed = run_nutrition_case(case)
    elif case.category == "training":
        obs, passed = run_training_case(case)
    elif case.category == "progress":
        obs, passed = run_progress_case(case)
    elif case.category == "safety":
        obs, passed = run_safety_case(case)
    elif case.category == "workflow":
        obs, passed = run_workflow_case(case)
    elif case.category == "api":
        obs, passed = run_api_case(case)
        
    return {
        "case_id": case.id,
        "category": case.category,
        "passed": passed,
        "score": 1.0 if passed else 0.0,
        "details": case.description,
        "observed": obs
    }

def run_eval_suite(cases: list[EvalCase] | None = None) -> dict:
    if cases is None:
        cases = get_default_eval_cases()
        
    results = []
    passed_count = 0
    
    for case in cases:
        res = run_eval_case(case)
        results.append(res)
        if res["passed"]:
            passed_count += 1
            
    total = len(cases)
    score = passed_count / total if total > 0 else 0.0
    
    return {
        "total": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "score": score,
        "results": results
    }

if __name__ == "__main__":
    from backend.evals.reporting import format_eval_report
    res = run_eval_suite()
    print(format_eval_report(res))
