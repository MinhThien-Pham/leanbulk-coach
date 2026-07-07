# Evaluation Plan — LeanBulk Coach

**Version**: 2.0  
**Status**: Active

---

## Evaluation Strategy

LeanBulk Coach utilizes a deterministic, local-first evaluation strategy:

1. **Unit Tests (`pytest`)**: Verifies calculations and safety limits inside `backend/tools/` with coverage analysis.
2. **Integration / Safety Evals (`backend/evals/runner.py`)**: Runs 12 integration cases covering nutrition, training, progress, safety, workflow, and API checks.

All tests run fully offline without any external LLM calls or API keys.

---

## Track 1 — Unit Tests

Located in: `backend/tests/unit/`

Run tests using:
```bash
pytest --tb=short -q
```

To run with coverage metrics:
```bash
pytest --cov=backend/tools --cov=backend/db --cov=backend/agents --cov=backend/mcp_server --cov=backend/workflows --cov=backend/app --cov=backend/evals --cov-report=term-missing -q
```

---

## Track 2 — Integration Evals (Eval Suite)

Located in: `backend/evals/`

Defined in: `backend/evals/cases.py`

Run the evaluation CLI suite using:
```bash
python -m backend.evals.runner
```

### Scoring and Evals
The suite executes 12 scenario checks. The run completes with an overall score showing pass/fail status per category (nutrition, training, progress, safety, workflow, api). All 12 cases must pass to pass the quality gate.
