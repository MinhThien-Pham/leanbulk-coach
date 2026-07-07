# AGENTS.md — LeanBulk Coach

Coding agent rules for this repository. All agents and contributors must follow these rules.
If code and docs disagree, fix the disagreement immediately — do not let drift accumulate.

---

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Agent framework | Google ADK (latest stable) | root agent + 5 sub-agents (compatibility config layer) |
| LLM | None required for demo | Current demo runs offline and deterministically |
| Backend | FastAPI + Uvicorn | Python 3.11+ |
| Database | SQLite via SQLAlchemy async | aiosqlite driver |
| MCP | `mcp` Python SDK (stdio transport) | Read-only context tools in MVP |
| Frontend | React + Vite | Dashboard, check-in, meal helper, dev panel |
| Testing | pytest + pytest-asyncio | All deterministic tools must have 100% coverage |
| Eval | Deterministic eval runner + pytest | See specs/EVAL_PLAN.md |
| Containers | Docker + docker-compose | Primary delivery artifact |

---

## Project Layout (Source of Truth)

```
leanbulk-coach/
├── .agents/skills/lean-bulk-coaching/   # Agent skill (SKILL.md + references/)
├── backend/
│   ├── agents/         # ADK root agent config + sub-agent configurations
│   ├── mcp_server/     # Read-only Model Context Protocol context tools
│   ├── app/            # FastAPI routes, schemas, and app configuration
│   ├── db/             # SQLAlchemy models, sessions, and repositories
│   ├── tools/          # Deterministic Python tools (pure functions, no LLM)
│   ├── workflows/      # Local demo flow and database seeding logic
│   ├── evals/          # Regression evaluation cases and reporting
│   └── tests/          # pytest unit + API integration tests
├── specs/              # Product spec, security, and demo scripts
├── frontend/           # React + Vite dashboard
├── .env.example        # Local demo configuration template
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
- No circular imports. Tools never import from agents/.

### Configuration
- Secret management is not required for the current offline demo.
- Runtime configuration is minimal and handled by the app/Docker environment.
- `.env.example` lists local database and port configurations.

---

## Hard Rules

1. **No medical diagnosis.** The agent MUST refuse to diagnose injuries, symptoms, or medical conditions. See `specs/SECURITY_GUARDRAILS.md`.
2. **No extreme dieting.** Never recommend a deficit > 500 kcal/day or a surplus > 600 kcal/day.
3. **No required live LLM for demo.** The active demo is fully offline and deterministic.
4. **No secrets in code.** Local runs operate fully offline without external API keys or tokens.
5. **MCP is read-only.** The MCP server exposes only read-only context tools (profile, body, nutrition, workout, meal, safety, and progress context). No write/update/delete MCP operations in MVP.
6. **Safety check before decision.** `safety_tools` must be called before any coaching summary is generated.
7. **Docs and code must agree.** If you change behavior that contradicts `specs/`, update the spec in the same commit.
8. **All deterministic tools must have pytest tests.** No exceptions.

---

## Safety Rules (Summary — full detail in specs/SECURITY_GUARDRAILS.md)

- `safety_tools.check_pain_flag()` runs before any training advice.
- `safety_tools.check_rate_of_change()` runs before any decision output.
- Calorie floor: 1400 kcal/day absolute minimum.
- Calorie ceiling: 6000 kcal/day absolute maximum.
- Weight gain safety limit: 0.45 kg/week for lean bulk.
- Waist creep threshold: 0.5 cm/week triggers a warning.
- Beginner training cap: 4 days/week maximum.

---

## Running Tests

No environment variables or API keys are required to run tests or evals.

```bash
# Unit tests
pytest backend/tests/unit/ -v

# With coverage
pytest backend/tests/unit/ -v --cov=backend/tools --cov-report=term-missing
```

## Running the Demo Backend

To start the API server locally:

```bash
uvicorn backend.app.main:app --reload --port 8000
```
