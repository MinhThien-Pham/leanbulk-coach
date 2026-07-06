from fastapi import APIRouter
from backend.app.schemas import EvalListResponse, EvalCaseSummary, EvalSuiteResponse, EvalReportResponse, EvalReportSummary
from backend.evals.cases import get_default_eval_cases
from backend.evals.runner import run_eval_suite
from backend.evals.reporting import format_eval_report

router = APIRouter()

@router.get("", response_model=EvalListResponse)
def list_evals():
    cases = get_default_eval_cases()
    return {
        "total": len(cases),
        "cases": [
            {"id": c.id, "category": c.category, "description": c.description}
            for c in cases
        ]
    }

@router.post("/run", response_model=EvalSuiteResponse)
def run_evals():
    res = run_eval_suite()
    return res

@router.get("/report", response_model=EvalReportResponse)
def get_eval_report():
    res = run_eval_suite()
    report_text = format_eval_report(res)
    return {
        "report": report_text,
        "summary": {
            "total": res["total"],
            "passed": res["passed"],
            "failed": res["failed"],
            "score": res["score"]
        }
    }
