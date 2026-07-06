# LeanBulk Coach

LeanBulk Coach is a safe, adaptive fitness agent designed specifically for skinny-fat beginners. It helps users decide whether to lean bulk, maintain, mini-cut, or deload based on weekly bodyweight trends, waist measurements, training performance, and adherence.

**Current Phase:** Phase 3A Complete (React/Vite frontend shell)

## Architecture Summary
Currently, the core logic is powered by deterministic Python tools that handle all math (TDEE, protein targets, trend analysis, safety checks) safely and predictably. A local SQLite persistence layer has been added for data storage. The AgentConfig layer defines the root + 5 sub-agent roles. An ADK adapter can export a root ADK agent without live LLM calls in tests. An MCP read-only server exposes context tools safely. A local deterministic demo flow connects tools, DB, MCP context, and coaching summary. FastAPI exposes deterministic tool, demo, summary, persistence, and context endpoints. A deterministic eval suite provides safety and quality regression testing, accessible through both the API and CLI.

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

### Running the Local API
You can run the FastAPI backend locally without an API key for deterministic endpoints:
```bash
uvicorn backend.app.main:app --reload
```
You can hit the evaluation report endpoint at:
`GET http://localhost:8000/evals/report`

### Running the Frontend
```bash
cd frontend
npm install
npm run dev
```
Note: Set `VITE_API_BASE_URL` if the backend is not running at `http://localhost:8000`.

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
