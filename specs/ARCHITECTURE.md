# Architecture — LeanBulk Coach

**Version**: 1.0  
**Status**: Active  
**Last Updated**: 2026-07-05

---

## System Overview

LeanBulk Coach is a locally-deployed multi-agent fitness coaching system. The architecture prioritises:
1. **Determinism first**: all numeric decisions (calories, protein, rate-of-change thresholds) computed by pure Python tools — no LLM math.
2. **LLM last**: the LLM writes the coach message and decision reasoning only after all tool outputs are assembled.
3. **Safety before output**: guardrail tools always run before the decision agent produces a response.
4. **Read-only MCP**: the MCP server exposes user history and coaching rules as read-only resources.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                              │
│                     React + Vite Frontend                           │
│   [Intake Form]  [Weekly Check-In]  [Dashboard]  [Meal Helper]      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/REST (localhost:5173 → :8000)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                FastAPI Backend  (port 8000)                         │
│   POST /intake   POST /checkin   POST /coaching/run                 │
│   GET  /dashboard/{user_id}      POST /meals/suggest                │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Guardrail Middleware                         │ │
│  │  • Pydantic v2 input validation (range checks, enum checks)   │ │
│  │  • Pre-request safety scan (extreme calorie/pain flags)       │ │
│  │  • API key authentication (single shared key from .env)       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                               │                                     │
│                               ▼                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Root Agent  (Google ADK)                         │ │
│  │  Model: $GEMINI_MODEL (from env)                              │ │
│  │  Pattern: sequential conditional pipeline                     │ │
│  │                                                               │ │
│  │  Step 1: IntakeAgent   → validate/hydrate user profile       │ │
│  │  Step 2: AnalysisAgent → compute trends + adherence          │ │
│  │  Step 3: safety_tools  → check_rate_of_change + pain_flag    │ │
│  │  Step 4: DecisionAgent → lean_bulk / mini_cut / maintain /   │ │
│  │                          deload + reasoning                   │ │
│  │  Step 5a: TrainingAgent → progression or deload protocol     │ │
│  │  Step 5b: MealAgent    → 2-3 meal suggestions                │ │
│  │  Step 6: Root Agent    → assemble + persist final response   │ │
│  │                                                               │ │
│  │  ── Deterministic Python Tools (backend/tools/) ──────────── │ │
│  │  calorie_tools  protein_tools  trend_tools                   │ │
│  │  safety_tools   progression_tools  meal_tools                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                               │                                     │
│            ┌──────────────────┴──────────────────┐                  │
│            ▼                                     ▼                  │
│  ┌─────────────────────┐            ┌──────────────────────────┐    │
│  │    SQLite DB         │            │      MCP Server          │    │
│  │  (SQLAlchemy async)  │◄──────────►│  (stdio transport)       │    │
│  │                      │            │  Spec: 2025-03-26        │    │
│  │  Tables:             │            │                          │    │
│  │  • users             │            │  Resources (read-only):  │    │
│  │  • check_ins         │            │  • user_history          │    │
│  │  • decisions         │            │  • coaching_rules        │    │
│  │  • meal_logs         │            │                          │    │
│  └─────────────────────┘            │  Tools (read-only):      │    │
│                                     │  • db_query_tool         │    │
│  ┌─────────────────────┐            │  • rules_lookup_tool     │    │
│  │   Memory Layers      │            └──────────────────────────┘    │
│  │                      │                                            │
│  │  Session: ADK        │            ┌──────────────────────────┐    │
│  │  InMemorySession     │            │    Knowledge Base         │    │
│  │                      │            │  (backend/knowledge_base/)│    │
│  │  Persistent: SQLite  │            │  • coaching_rules.json   │    │
│  │  (check-ins +        │            │  • safe_rate_tables.json │    │
│  │   decisions history) │            └──────────────────────────┘    │
│  └─────────────────────┘                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Sub-Agent Responsibilities

### IntakeAgent
- **Trigger**: New user onboarding or profile update
- **Tools called**: `calorie_tools.calc_tdee`, `protein_tools.calc_protein_target`
- **Output**: Hydrated user profile with computed baseline TDEE and protein target
- **MCP**: Reads `user_history` to detect returning users

### AnalysisAgent
- **Trigger**: Every weekly check-in submission
- **Tools called**: `trend_tools.weight_trend`, `trend_tools.waist_trend`, `trend_tools.adherence_score`
- **Output**: Structured trend summary (weight delta, waist delta, adherence %)
- **MCP**: Reads `user_history` for previous week's data

### DecisionAgent
- **Trigger**: After AnalysisAgent output and safety checks pass
- **Tools called**: (none directly — receives tool outputs from pipeline)
- **MCP**: Calls `rules_lookup_tool` to fetch the relevant coaching rule subset
- **LLM role**: Interprets combined tool outputs + rules → produces decision + reasoning
- **Output**: One of 5 decisions + calorie/protein targets + reasoning string

### TrainingAgent
- **Trigger**: After DecisionAgent (always, but in deload mode if DELOAD decision)
- **Tools called**: `progression_tools.suggest_weekly_progression`, `safety_tools.check_pain_flag`
- **Output**: Per-exercise progression recommendation or deload protocol

### MealAgent
- **Trigger**: After DecisionAgent (parallel with TrainingAgent)
- **Tools called**: `meal_tools.suggest_meals`
- **MCP**: Reads user preferences from `user_history`
- **Output**: 2–3 meal suggestions with macros

---

## Data Models (SQLite)

```
users
  id            TEXT PRIMARY KEY  (UUID)
  created_at    DATETIME
  age           INTEGER
  sex           TEXT
  height_cm     REAL
  weight_kg     REAL
  waist_cm      REAL
  training_level TEXT
  primary_goal  TEXT
  training_days INTEGER
  equipment     TEXT (JSON array)
  dietary_prefs TEXT (JSON array)
  injury_notes  TEXT

check_ins
  id            TEXT PRIMARY KEY
  user_id       TEXT REFERENCES users(id)
  week_start    DATE
  submitted_at  DATETIME
  avg_weight_kg REAL
  waist_cm      REAL
  avg_calories  INTEGER
  avg_protein_g INTEGER
  workouts_done INTEGER
  workouts_planned INTEGER
  lifts_log     TEXT (JSON)
  avg_sleep_h   REAL
  energy_level  INTEGER
  notes         TEXT

decisions
  id            TEXT PRIMARY KEY
  check_in_id   TEXT REFERENCES check_ins(id)
  user_id       TEXT
  created_at    DATETIME
  decision      TEXT
  reasoning     TEXT
  calorie_target INTEGER
  protein_target INTEGER
  training_note TEXT
  coach_message TEXT
  safety_warning TEXT

meal_logs
  id            TEXT PRIMARY KEY
  user_id       TEXT
  logged_at     DATETIME
  meal_name     TEXT
  kcal          INTEGER
  protein_g     INTEGER
```

---

## MCP Server Design

**Transport**: stdio (no network port; runs as subprocess)  
**Spec version**: 2025-03-26  
**Constraint**: Read-only MVP. No create/update/delete tools.

### Resources
| URI pattern | Description | Returns |
|---|---|---|
| `leanbulk://users/{user_id}/history?limit=N` | Last N check-ins + decisions | JSON |
| `leanbulk://knowledge/rules` | Full coaching_rules.json | JSON |

### Tools
| Tool | Arguments | Returns |
|---|---|---|
| `db_query_tool` | `user_id: str, query_type: str, limit: int` | Structured check-in or decision history |
| `rules_lookup_tool` | `scenario: str` | Matching coaching rule subset from knowledge_base |

---

## Configuration (Environment Variables)

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | Google AI API key |
| `GEMINI_MODEL` | Yes | — | Model name, e.g. `gemini-2.0-flash-001` |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./leanbulk.db` | SQLite DB path |
| `API_KEY` | Yes | — | Shared key for backend API authentication |
| `MCP_SERVER_PATH` | No | `backend/mcp/server.py` | Path to MCP server script |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Allowed CORS origins |

---

## Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Sync vs async | Async FastAPI + aiosqlite | Non-blocking I/O; ADK sessions are concurrent |
| ORM | SQLAlchemy 2.x async | Modern API, well-supported, no Postgres needed |
| Schema validation | Pydantic v2 | ADK requires Pydantic v2; best-in-class validation |
| MCP transport | stdio | Local-only MVP; no auth surface; simple subprocess management |
| Model flexibility | Env var `GEMINI_MODEL` | Allows flash (dev) vs pro (eval/demo) without code changes |
| Frontend | React + Vite | Fastest setup, good ecosystem, easy to make polished |
| Charts | Recharts | Composable, well-documented, works well with React |
