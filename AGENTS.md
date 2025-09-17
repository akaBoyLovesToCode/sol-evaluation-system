# Repository Guidelines

## Project Structure & Module Organization
- `backend/` – Flask API (SQLAlchemy, JWT, SocketIO). Tests in `backend/tests/`.
- `frontend/` – Vue 3 + Vite app. Tests in `frontend/tests/`.
- `mysql/` – Local DB volume/config; `terraform/` – infra definitions.
- `docker-compose.yml` – Local multi‑service stack (frontend, backend, MySQL, Jaeger).

## Build, Test, and Development Commands
Backend (Python 3.13):
- Install: `cd backend && pip install -r requirements.txt` (or `uv pip sync requirements.txt`).
- Lint/format: `ruff check .` and `ruff format .`.
- Run dev: `python run.py` or `flask run --host=0.0.0.0 --port=5001`.
- Tests: `pytest --cov=app tests/ -v` (markers: `-m unit|integration|api`).

Frontend (Node 22):
- Install: `cd frontend && npm ci`.
- Dev server: `npm run dev` (Vite).
- Build: `npm run build` · Preview: `npm run preview`.
- Lint/format: `npm run lint` · `npm run format:check`/`npm run format`.
- Tests: `npm test` or `npm run test:coverage`.

Docker (full stack):
- From repo root: `docker compose up --build -d`.

## Coding Style & Naming Conventions
Backend (Python):
- 4‑space indent, snake_case for functions/vars, PascalCase for classes.
- Use `ruff` for linting and formatting; keep imports and typing clean.

Frontend (Vue/JS):
- 2‑space indent. Prettier config: semi=false, singleQuote=true, width=100.
- Component files PascalCase (e.g., `UserCard.vue`); routes named in PascalCase.
- ESLint Vue rules enforce component name casing and no unused vars.

## Testing Guidelines
Backend: Pytest in `backend/tests/` with `test_*.py`. Prefer unit tests under `tests/unit/`. Use fixtures in `conftest.py`. Generate coverage XML for CI: `pytest --cov=app --cov-report=xml`.

Frontend: Jest + @testing-library/vue. Place specs in `frontend/tests/` as `*.spec.js`. Keep components testable (props in, events out).

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor(nginx):`, `ci(deploy):`, `chore:`; add scope when helpful (e.g., `fix(frontend): ...`).
- PRs: include a clear description, linked issues (`Closes #123`), relevant screenshots for UI changes, and notes on testing. Ensure CI (lint, tests, coverage, build) passes.

## Security & Configuration Tips
- Do not commit secrets; use `.env` files (see `backend/.env` example) and `DATABASE_URL` for overrides. For local DB, rely on `docker-compose.yml` defaults.
