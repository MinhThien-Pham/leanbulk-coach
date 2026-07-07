# Architecture — LeanBulk Coach

**Version**: 2.0  
**Status**: Active  
**Last Updated**: 2026-07-06

---

## System Overview

LeanBulk Coach is an offline-first, safety-oriented coaching assistant. The architecture prioritises:
1. **Determinism first**: all numeric decisions (calories, protein, rate-of-change thresholds) are computed by pure Python tools—no live LLM calculations are required.
2. **Safety before output**: guardrail tools are always executed before generating coaching summaries.
3. **Read-only MCP**: the Model Context Protocol context server exposes read-only user metrics and logs.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                              │
│                     React + Vite Frontend                           │
│   [Onboarding Form]  [Check-In Panel]  [Dashboard]  [Meal Helper]   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/REST (localhost:5173 → :8000)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                FastAPI Backend  (port 8000)                         │
│   POST /profiles      POST /logs/body      POST /logs/workouts      │
│   POST /logs/meals    GET /context/{id}    POST /summary/build      │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   Guardrail Middleware                         │ │
│  │  • Pydantic v2 input validation (range checks, enum checks)   │ │
│  │  • Pre-request safety scan (extreme calorie/pain flags)       │ │
│  │  └────────────────────────────────────────────────────────────────┘ │
│                               │                                     │
│                               ▼                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Root Agent  (Google ADK Config)                  │ │
│  │  Runtime: local deterministic tools                           │ │
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
│  │  └────────────────────────────────────────────────────────────────┘ │
│                               │                                     │
│            ┌──────────────────┴──────────────────┐                  │
│            ▼                                     ▼                  │
│  ┌─────────────────────┐            ┌──────────────────────────┐    │
│  │    SQLite DB         │            │      MCP Server          │    │
│  │  (SQLAlchemy async)  │◄──────────►│  (stdio transport)       │    │
│  │                      │            │  Spec: 2025-03-26        │    │
│  │  Tables:             │            │                          │    │
│  │  • profiles          │            │  Read-Only Tools:        │    │
│  │  • body_metric_logs  │            │  • read_profile_context  │    │
│  │  • workout_set_logs  │            │  • read_latest_body      │    │
│  │  • meal_logs         │            │  • read_body_history     │    │
│  │  • safety_flag_logs  │            │  • read_recent_meals     │    │
│  │  • nutrition_targets │            │  • read_recent_workouts  │    │
│  └─────────────────────┘            └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### Deterministic Core Tools (`backend/tools/`)
The current MVP uses pure functions for all calculations:
- `calorie_tools`: Maintenance, surplus, and deficit target math.
- `protein_tools`: Goal-based target calculations.
- `safety_tools`: Clamping and active warning guardrails.
- `trend_tools`: Multi-day chronological regression analysis.

### Persistence Layer (`backend/db/`)
- SQLite database wrapper managed asynchronously via SQLAlchemy.
- Tables include `profiles`, `body_metric_logs`, `workout_set_logs`, `meal_logs`, `safety_flag_logs`, and `nutrition_target_logs`.

---

## Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Sync vs async | Async FastAPI + aiosqlite | Non-blocking database operations |
| ORM | SQLAlchemy 2.x async | Modern API, SQLite support |
| Schema validation | Pydantic v2 | Standard validation models |
| MCP transport | stdio | Local subprocess execution |
| Frontend | React + Vite | Clean dev setup, custom HTML/CSS charts (no charting library dependency) |
