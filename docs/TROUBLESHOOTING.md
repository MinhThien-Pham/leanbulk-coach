# Troubleshooting Guide - LeanBulk Coach

This guide lists common setup issues, configuration errors, and fixes.

---

## 1. Port 8000 or 5173 Already in Use

### Symptom:
FastAPI or Vite fails to start with errors like `ADDRINUSE` or `Port already in use`.

### Fixes:
1. **Find and terminate the occupying process:**
   - **On Windows (PowerShell):**
     ```powershell
     Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
     Get-NetTCPConnection -LocalPort 5173 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
     ```
   - **On macOS/Linux:**
     ```bash
     lsof -t -i:8000 | xargs kill -9
     lsof -t -i:5173 | xargs kill -9
     ```
2. **Or configure alternative ports:**
   - For backend, start uvicorn with:
     ```bash
     uvicorn backend.app.main:app --port 8080
     ```
   - For frontend, edit `frontend/vite.config.js` or start it with:
     ```bash
     npm run dev -- --port 5174
     ```
   - Update `VITE_API_BASE_URL` in the frontend environment variables to match the new backend port.

---

## 2. Frontend Cannot Reach Backend (CORS Error)

### Symptom:
Clicking buttons in the frontend has no effect, or the console shows `Access-Control-Allow-Origin` errors.

### Fixes:
- **CORS configuration is strict:** The backend whitelist is hard-coded to allow:
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`
  - `http://localhost:5174`
  - `http://127.0.0.1:5174`
- Make sure you are accessing the frontend using one of these exact addresses. If you run the frontend on a different port or custom host (like your local network IP), add it to the `CORSMiddleware` setup in `backend/app/main.py`.

---

## 3. Database Out of Sync or SQLite File Lock

### Symptom:
SQLAlchemy throws errors regarding missing tables, column mismatches, or locked databases.

### Fixes:
- **Initialize/reset database manually:**
  Delete the local database file `leanbulk_api.db` in your root or backend folder and restart the app. The app automatically rebuilds the tables on startup if they don't exist.
- **Docker database location:**
  Inside Docker Compose, the database is persisted in a volume named `leanbulk_data`. To completely wipe and rebuild it:
  ```bash
  docker compose down -v
  docker compose up --build
  ```

---

## 4. npm ci Fails

### Symptom:
`npm ci` fails with lockfile or compatibility warnings.

### Fixes:
- `npm ci` requires an exact match between `package.json` and `package-lock.json`. If you modified any dependencies, run `npm install` first to update the lockfile before running `npm ci` again.
- Clear npm caches:
  ```bash
  npm cache clean --force
  ```

---

## 5. Python Dependency Install Errors (e.g. greenlet or uvicorn build issues)

### Symptom:
`pip install -r backend/requirements.txt` fails when compiling binary extensions (like greenlet or uvloop).

### Fixes:
- Make sure you have python headers installed (`python3-dev` on Ubuntu/Debian).
- Ensure your pip version is upgraded to compile standard pre-built wheels:
  ```bash
  python -m pip install --upgrade pip setuptools wheel
  ```
- If compiling `uvloop` fails on Windows, note that `uvloop` is only used on UNIX-based systems. The backend will automatically fall back to standard asyncio event loops on Windows.

---

## 6. GitHub Actions Workflows Not Triggering

### Symptom:
Pushing to a branch does not start the CI runs.

### Fixes:
- Verify the workflow configuration file is named exactly `.github/workflows/ci.yml`.
- Verify the branch name matches the trigger list (defaults to `main`).
