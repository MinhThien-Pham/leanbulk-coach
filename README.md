# LeanBulk Coach

LeanBulk Coach is a safe, adaptive fitness agent designed specifically for skinny-fat beginners. It helps users decide whether to lean bulk, maintain, mini-cut, or deload based on weekly bodyweight trends, waist measurements, training performance, and adherence.

**Current Phase:** Phase 1A.1 Complete (Cleanup & Deterministic Tools)

## Architecture Summary
Currently, the core logic is powered by deterministic Python tools that handle all math (TDEE, protein targets, trend analysis, safety checks) safely and predictably. Later phases will introduce a Google ADK root agent orchestrating several sub-agents, driven by an MCP read-only server and SQLite persistence.

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

### Running Tests
The project relies on deterministic tool testing with 100% coverage via `pytest`.
```bash
pytest --tb=short -q
pytest --cov=backend/tools --cov-report=term-missing -q
```
**Current Status:** 193/193 tests passing with 100% coverage.

## ⚠️ Safety & Guardrails
**Not Medical Advice:** LeanBulk Coach provides general fitness guidance and is not a substitute for professional medical advice, diagnosis, or treatment. It contains strict guardrails that block extreme calorie deficits/surpluses, flag unsafe rate-of-change trends (e.g. waist creep), and refuse medical diagnosis requests. Always consult a healthcare professional for medical issues.

## Roadmap
- **Phase 1B:** Google ADK agents, MCP read-only server, SQLite persistence.
- **Phase 2:** FastAPI backend and advanced evaluation harnesses.
- **Phase 3:** React + Vite frontend and Docker Compose deployment.
