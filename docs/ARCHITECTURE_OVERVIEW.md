# Architecture Overview - LeanBulk Coach

This document details the system design, core modules, and testing strategy for LeanBulk Coach.

## System Topology

```
+-----------------------------------------------------------------------------------+
|                                  React Frontend                                   |
|                        (onboarding, check-in, dashboard)                          |
+-----------------------------------------------------------------------------------+
                                         |
                                    (HTTP APIs)
                                         v
+-----------------------------------------------------------------------------------+
|                                   FastAPI API                                     |
|           (routes/profiles.py, routes/logs.py, routes/summary.py, etc.)           |
+-----------------------------------------------------------------------------------+
                                         |
               +-------------------------+-------------------------+
               |                                                   |
               v                                                   v
+-----------------------------+                     +-------------------------------+
|         MCP Server          |                     |     Coaching Workflows        |
|     (read-only context      |                     |   (seed_demo_data.py,         |
|           tools)            |                     |    demo_flow.py)              |
+-----------------------------+                     +-------------------------------+
               |                                                   |
               v                                                   v
+-----------------------------+                     +-------------------------------+
|      SQLite Database        |                     |      Deterministic Tools      |
|  (SQLAlchemy models, repo)  |                     | (calorie_tools, safety_tools) |
+-----------------------------+                     +-------------------------------+
```

---

## Core Components

### 1. Deterministic Core Tools (`backend/tools/`)
The MVP uses **pure, side-effect-free functions** for all calculations:
- `calorie_tools`: Implements Harris-Benedict formulas and activity multipliers.
- `protein_tools`: Implements protein targets based on lean mass and goal.
- `safety_tools`: Handles guardrails (caps on daily calories, training frequency, and waist creep warnings).
- `trend_tools`: Evaluates weight averages and waist measurement progression.

By using pure functions, the logic is highly testable, runs with sub-millisecond execution times, and requires **no external network connections or API keys**.

### 2. Persistence Layer (`backend/db/`)
Utilizes an asynchronous SQLite database wrapper managed via SQLAlchemy:
- `models.py`: Declares tables for `UserProfile`, `BodyMetricLog`, `WorkoutSetLog`, `NutritionTargetLog`, `MealLog`, and `SafetyFlagLog`.
- `repositories.py`: Contains CRUD functions matching FastAPI routes.
- `session.py`: Manages the database connection pool using the `aiosqlite` async driver.

### 3. MCP Context Server (`backend/mcp_server/`)
Implements the Model Context Protocol (MCP) server:
- Operates strictly in a **read-only** manner.
- Exposes read-only context tools for retrieving:
  - User profile details (`read_profile_context`)
  - Latest body weight and waist measurement (`read_latest_body_context`)
  - Historical weight trend logs (`read_body_history_context`)
  - Calorie and protein targets (`read_latest_nutrition_context`)
  - Resistance training set logs (`read_recent_workout_context`)
  - Nutrition meal entry logs (`read_recent_meal_context`)
  - Active injury flags and pain logs (`read_open_safety_context`)
  - Rolling average trend calculations (`read_progress_summary_context`)

### 4. ADK-Compatible Agent Layer (`backend/agents/`)
Utilizes the Google Agent Development Kit (ADK) config structures:
- Configures a parent root agent coordinating 5 specialized sub-agents: `IntakeAgent`, `ProgressAgent`, `TrainingAgent`, `NutritionAgent`, and `SafetyAgent`.
- Registers deterministic fallback tools for mock runs.

### 5. FastAPI Backend Shell (`backend/app/`)
Exposes HTTP endpoints for:
- Database inserts (adding weights, workouts, meals, and safety flags).
- Building coaching summaries (`POST /summary/build`).
- Running the evaluation regression suite (`POST /evals/run` and `GET /evals/report`).

### 6. React Frontend (`frontend/`)
- A modular dashboard containing panels for profile creation, weekly metric check-ins, custom trend charts, and the daily meal helper.
- Standardized to use plain ASCII text to avoid browser text-encoding issues.

---

## Safety Guardrails & Testing Strategy

### Why Emojis / Live Calls Are Avoided in Core Workflows
1. **Rule-Based Safety:** Live LLM responses can hallucinate recommendations or fail to enforce guardrails. By routing the final decision summary through deterministic, rule-based tools, we ensure that the client never receives an extreme diet recommendation (e.g., calorie deficit > 500 kcal or surplus > 600 kcal) or unsafe training advice during active injury flags.
2. **Reliable Testability:** Offline execution ensures tests never fail due to model rate limits, service deprecation, or billing issues.

### Safety Regression Testing (Eval Suite)
The evaluation suite (`backend/evals/runner.py`) uses 12 deterministic check-in scenarios (e.g., progress checks, meal preferences, joint pain flags, waist creep warnings) to run end-to-end integration tests:
- Automatically validates the system against safety limits (e.g., verifying a knee pain flag suspends squat progression).
- Fully integrated into pytest and the local API endpoints for easy review.
