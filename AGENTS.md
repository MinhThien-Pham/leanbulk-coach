# AGENTS.md — LeanBulk Coach

Coding agent rules for this repository. All agents and contributors must follow these rules.
If code and docs disagree, fix the disagreement immediately — do not let drift accumulate.

---

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Agent framework | Google ADK (latest stable) | root agent + 5 sub-agents |
| LLM | Gemini (model via `GEMINI_MODEL` env var) | Never hardcode a model name |
| Backend | FastAPI + Uvicorn | Python 3.11+ |
| Database | SQLite via SQLAlchemy async | aiosqlite driver |
| MCP | `mcp` Python SDK (stdio transport) | Read-only in MVP |
| Frontend | React + Vite | Phase 3 only |
| Testing | pytest + pytest-asyncio | All deterministic tools must have 100% coverage |
| Eval | ADK-native eval files + pytest | See specs/EVAL_PLAN.md |
| Containers | Docker + docker-compose | Primary delivery artifact |

---

## Project Layout (Source of Truth)

```
leanbulk-coach/
├── .agents/skills/lean-bulk-coaching/   # Agent skill (SKILL.md + references/)
├── backend/
│   ├── agent/          # ADK root agent + sub-agents + prompts + memory
│   ├── mcp/            # MCP server, resources, tools
│   ├── api/            # FastAPI routers, schemas, middleware
│   ├── db/             # SQLAlchemy models, migrations
│   ├── tools/          # Deterministic Python tools (no LLM)
│   ├── knowledge_base/ # coaching_rules.json, safe_rate_tables.json
│   ├── evals/          # ADK eval cases, fixtures
│   └── tests/          # pytest unit + integration tests
├── specs/              # Product spec, architecture, eval plan, security, demo script
├── frontend/           # React + Vite (Phase 3)
├── .env.example        # Template — never commit real secrets
├── AGENTS.md           # This file
└── README.md
```

---

## Conventions

### Python
- Python 3.11+. Use type hints everywhere.
- `backend/tools/` contains **only pure functions** — no I/O, no LLM calls, no side effects.
- All tools must be importable without any environment variables set.
- Use `dataclasses` or typed `dict` for tool return values. No bare dicts without TypedDict annotations.
- Format: `black` + `isort`. Max line length 99.
- Docstrings on every public function. Google style.

### Naming
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- ADK agents: suffix with `Agent` (e.g. `IntakeAgent`, `DecisionAgent`)
- ADK tools: suffix with `_tool` when registered as an ADK tool function

### Imports
- Absolute imports from `backend.*` package root.
- No circular imports. Tools never import from agent/.

### Configuration
- All secrets and tuneable parameters come from environment variables.
- Load env vars with `python-dotenv` in a single `backend/config.py` module.
- `.env.example` is the canonical list of all required env vars.
- **Never hardcode API keys, model names, or database paths in source code.**

---

## Hard Rules

1. **No medical diagnosis.** The agent MUST refuse to diagnose injuries, symptoms, or medical conditions. See `specs/SECURITY_GUARDRAILS.md`.
2. **No extreme dieting.** Never recommend a deficit > 500 kcal/day or a surplus > 600 kcal/day.
3. **No hardcoded model names.** Always read `GEMINI_MODEL` from environment.
4. **No secrets in code.** API keys, tokens, passwords live in `.env` only. `.env` is gitignored.
5. **MCP is read-only.** `db_query_tool` and `rules_lookup_tool` are the only MCP tools. No write/update/delete MCP operations in MVP.
6. **Safety check before decision.** `safety_tools` must be called before any `DecisionAgent` output.
7. **Docs and code must agree.** If you change behavior that contradicts `specs/`, update the spec in the same commit.
8. **All deterministic tools must have pytest tests.** No exceptions.

---

## Workflow

### Phase 1A — Foundation (Current)
- Deterministic tools + unit tests
- Spec documents
- `.env.example`, `.gitignore`, `requirements.txt`
- Agent Skill (`SKILL.md`)

### Phase 1B — Agent + MCP
- ADK root agent + 5 sub-agents
- MCP server (read-only)
- SQLite DB models + migrations
- Memory layer

### Phase 2 — API + Eval
- FastAPI routers + guardrail middleware
- ADK eval cases (final output + tool trajectory)
- Docker + docker-compose

### Phase 3 — Frontend
- React + Vite UI
- Onboarding, check-in, dashboard, meal helper pages

---

## Safety Rules (Summary — full detail in specs/SECURITY_GUARDRAILS.md)

- Every coaching output must include the medical disclaimer.
- `safety_tools.check_pain_flag()` runs before any training advice.
- `safety_tools.check_rate_of_change()` runs before any decision output.
- Calorie floor: 1400 kcal/day absolute minimum.
- Calorie ceiling: 6000 kcal/day absolute maximum.
- Weight gain safety limit: 0.45 kg/week for lean bulk.
- Waist creep threshold: 0.5 cm/week triggers a warning.
- Beginner training cap: 4 days/week maximum.

---

## Running Tests

```bash
# Unit tests (deterministic tools only — no env vars required)
pytest backend/tests/unit/ -v

# With coverage
pytest backend/tests/unit/ -v --cov=backend/tools --cov-report=term-missing
```

## Running the Agent (Phase 1B+)

```bash
# Requires .env with GEMINI_API_KEY and GEMINI_MODEL set
uvicorn backend.api.main:app --reload --port 8000
```
