# LeanBulk Coach

LeanBulk Coach is a safe, adaptive fitness agent designed specifically for skinny-fat beginners. It helps users decide whether to lean bulk, maintain, mini-cut, or deload based on weekly bodyweight trends, waist measurements, training performance, and adherence.

**Current Phase:** Phase 4A Complete (local Docker orchestration)

## Architecture Summary
Currently, the core logic is powered by deterministic Python tools that handle all math (TDEE, protein targets, trend analysis, safety checks) safely and predictably. A local SQLite persistence layer has been added for data storage. The AgentConfig layer defines the root + 5 sub-agent roles. An ADK adapter can export a root ADK agent without live LLM calls in tests. An MCP read-only server exposes context tools safely. A local deterministic demo flow connects tools, DB, MCP context, and coaching summary. FastAPI exposes deterministic tool, demo, summary, persistence, context, seed, and evaluation endpoints. A deterministic eval suite provides safety and quality regression testing, accessible through both the API and CLI. The React + Vite frontend supports onboarding profile creation, weekly check-ins, persisted body/workout/meal/safety logs, dashboard context view, the meal helper, a deterministic sample-data seed workflow, and a local Docker Compose development orchestration.

## Getting Started

### Installation
1. Ensure you have Python 3.11+ installed.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

### Running with Docker Compose (Local Demo Only)
To build and run the entire stack with a single command:
```bash
docker compose up --build
```
Once started, the application services will be available at:
- Backend Health Check: `GET http://localhost:8000/health`
- Frontend UI: `http://localhost:5173`

*Note: The Docker Compose setup is strictly optimized for local development and review, and is not configured for production deployment.*

### Running the Local API (Manually)
You can run the FastAPI backend locally without an API key for deterministic endpoints:
```bash
uvicorn backend.app.main:app --reload
```
You can hit the evaluation report endpoint at:
`GET http://localhost:8000/evals/report`

### Running the Frontend (Manually)
```bash
cd frontend
npm install
npm run dev
```
Note: Set `VITE_API_BASE_URL` if the backend is not running at `http://localhost:8000`.

### 2-Minute Demo Workflow
1. Start the services (either via Docker Compose or manually).
2. Open the Frontend UI, select the **Onboarding** tab, and click **Create Demo Profile** to seed a complete mock user history.
3. Navigate to the **Dashboard**, **Meal Helper**, or **Dev Panel** to explore the seeded metrics, trend charts, next actions, safety flags, and evaluation reports.

### Running the CLI Eval Report
```bash
python -m backend.evals.runner
```

### Running Tests
The project relies on deterministic offline testing with high coverage via `pytest`.
```bash
pytest --tb=short -q
pytest --cov=backend/tools --cov=backend/db --cov=backend/agents --cov=backend/mcp_server --cov=backend/workflows --cov=backend/app --cov=backend/evals --cov-report=term-missing -q
```
**Current Status:** All deterministic tool, database, agent structure, MCP context, workflow, persistence API, and evaluation API tests are passing with high coverage. No live LLM calls in tests.

## ⚠️ Safety & Guardrails
**Not Medical Advice:** LeanBulk Coach provides general fitness guidance and is not a substitute for professional medical advice, diagnosis, or treatment. It contains strict guardrails that block extreme calorie deficits/surpluses, flag unsafe rate-of-change trends (e.g. waist creep), and refuse medical diagnosis requests. Always consult a healthcare professional for medical issues.

## Roadmap
- **Phase 2:** FastAPI backend and advanced evaluation harnesses.
- **Phase 3:** React + Vite frontend and Docker Compose deployment.
