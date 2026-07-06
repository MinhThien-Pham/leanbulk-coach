# Demo Script — LeanBulk Coach

**Version**: 1.0  
**Purpose**: Step-by-step walkthrough for Kaggle submission demo, grader review, or live presentation.

---

## Prerequisites

- Docker Compose running (`docker compose up`) OR local quickstart active
- Backend available at `http://localhost:8000`
- (Phase 3) Frontend available at `http://localhost:5173`
- Valid `.env` with `GEMINI_API_KEY` and `GEMINI_MODEL` set

---

## Demo Flow (10-minute script)

### Step 1 — Show the Architecture (1 min)
Open `specs/ARCHITECTURE.md` and walk through:
- 5 sub-agents and their responsibilities
- MCP server as read-only knowledge/history interface
- Deterministic tools vs LLM roles
- Safety guardrail layers

### Step 2 — Swagger UI Tour (1 min)
Navigate to `http://localhost:8000/docs`

Show all endpoints:
- `POST /intake` — intake form submission
- `POST /checkin` — weekly check-in
- `POST /coaching/run` — trigger agent pipeline
- `GET /dashboard/{user_id}` — progress data
- `POST /meals/suggest` — meal helper

### Step 3 — New User Intake (1 min)
Submit a `POST /intake` request using the happy path profile:

```json
{
  "age": 24,
  "sex": "male",
  "height_cm": 175,
  "weight_kg": 72,
  "waist_cm": 85,
  "training_level": "beginner",
  "primary_goal": "lean_bulk",
  "training_days": 3,
  "equipment": ["barbell", "dumbbells"],
  "dietary_prefs": [],
  "injury_notes": ""
}
```

Point out: Pydantic validation, TDEE calculated, profile persisted.

### Step 4 — Weekly Check-In + Agent Decision (3 min)
Submit `POST /coaching/run` with this happy-path check-in:

```json
{
  "user_id": "<id from step 3>",
  "avg_weight_kg": 72.2,
  "waist_cm": 84.8,
  "avg_calories": 2850,
  "avg_protein_g": 165,
  "workouts_done": 3,
  "workouts_planned": 3,
  "lifts_log": [
    {"exercise": "Squat", "weight_kg": 60, "reps": 5},
    {"exercise": "Bench Press", "weight_kg": 52.5, "reps": 5}
  ],
  "avg_sleep_h": 7.5,
  "energy_level": 4,
  "notes": "Feeling good this week!"
}
```

Walk through the response:
- `decision: LEAN_BULK_CONTINUE`
- `calorie_target`, `protein_target`
- `training_recommendation` (progression)
- `coach_message`
- `medical_disclaimer` (always present)

Show agent logs to demonstrate tool call trajectory.

### Step 5 — Guardrail Demo: Extreme Cut (2 min)
Submit `POST /coaching/run` with same user but notes:

```json
"notes": "I want to cut 1000 calories this week and lose 2kg fast"
```

Show response:
- `decision: GUARDRAIL_TRIGGERED`
- `safety_warning` present
- `calorie_target` is NOT 1000 kcal deficit
- Coach message redirects appropriately

### Step 6 — Medical Guardrail Demo (1 min)
Submit with notes:

```json
"notes": "I think I have a hernia. Should I still do squats?"
```

Show response:
- Hard block on training advice
- Medical disclaimer in `safety_warning`
- Redirect to healthcare professional

### Step 7 — Meal Helper (1 min)
Submit `POST /meals/suggest`:

```json
{
  "user_id": "<id>",
  "remaining_kcal": 600,
  "remaining_protein_g": 35,
  "dietary_prefs": [],
  "equipment": ["stove", "microwave"]
}
```

Show 2-3 meal suggestions with macros.

---

## Key Concepts to Call Out

| Concept | Where it appears in demo |
|---|---|
| Multi-agent system (ADK) | Step 4 — root agent orchestrates 5 sub-agents |
| Tool use | Step 4 — deterministic tools shown in logs |
| Memory/context | Step 4 — MCP reads previous check-in history |
| MCP server | Step 4/7 — `rules_lookup_tool` and `db_query_tool` |
| Agent Skill | Architecture diagram — `SKILL.md` guides workflow |
| Evaluation | Run `pytest` + `adk eval` live or show screenshot |
| Security/guardrails | Steps 5 & 6 |
| Deployability | Show `docker compose up` working |

---

## Running the Eval Suite for Demo

```bash
# Deterministic tool tests (fast, no API key needed)
pytest backend/tests/unit/ -v --tb=short

# ADK agent evals (requires GEMINI_API_KEY)
adk eval backend/agent/root_agent.py backend/evals/cases/ --config backend/evals/eval_config.json
```

Expected output: ≥ 4/6 cases pass, 0 safety failures.

---

## Troubleshooting Common Demo Issues

| Issue | Fix |
|---|---|
| `GEMINI_API_KEY not set` | Copy `.env.example` to `.env` and add your key |
| `GEMINI_MODEL not set` | Add `GEMINI_MODEL=gemini-2.0-flash-001` to `.env` |
| Port 8000 in use | Change `PORT=8000` in `.env` |
| Docker build fails | Ensure Docker Desktop is running, then `docker compose build --no-cache` |
| adk eval not found | Run `pip install google-adk` and ensure venv is active |
