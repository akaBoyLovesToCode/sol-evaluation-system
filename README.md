# Solution Evaluation System (Simplified)

A streamlined web app for managing product evaluations. This version removes authentication, users, notifications, and dashboards, focusing on the core: evaluations, processes, and status management with IP-based logging.

## Features
- Evaluation CRUD (two types: new_product, mass_production)
- Processes per evaluation (eval_code, lot_number, quantity, descriptions, results)
- Status lifecycle (draft, in_progress, pending_part_approval, pending_group_approval, completed, paused, cancelled, rejected) — approvals not enforced
- IP‑based operation logs (request method, path, query, user agent)
- Blue‑themed, minimal frontend with a clean topbar and language selector

## Tech Stack
- Frontend: Vue 3, Vite, Element Plus, Vue Router, Vue I18n
- Backend: Flask, SQLAlchemy, Alembic, Flask‑CORS
- Database: MySQL 8

## Installation

### Backend (auth‑less)
```bash
cd backend
uv pip sync requirements.txt
# configure .env (MySQL connection)
flask db upgrade
flask init-db
python run.py
```
Backend runs at `http://localhost:5001`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`.

## Public API (no auth)
- `GET /api/evaluations` – list (filters: status, evaluation_type, product_name, scs_charger_name, head_office_charger_name, page, per_page)
- `GET /api/evaluations/{id}` – detail (includes processes, logs)
- `POST /api/evaluations` – create (auto‑generates evaluation_number if omitted)
- `PUT /api/evaluations/{id}` – update
- `DELETE /api/evaluations/{id}` – delete
- `GET/POST /api/evaluations/{id}/processes`
- `GET/PUT/DELETE /api/evaluations/{id}/processes/{process_id}`
- `PUT /api/evaluations/{id}/status`
- `GET /api/evaluations/{id}/logs`

## Frontend Structure (trimmed)
```
frontend/src/
  views/
    Evaluations.vue         # root view (list)
    NewEvaluation.vue       # create/edit
    EvaluationDetail.vue    # detail + processes + logs
  components/
    AnimatedContainer.vue
  router/
    index.js
  utils/
    api.js                  # no auth headers; unified error handling
```

## Notes
- Chargers are free‑text: `scs_charger_name`, `head_office_charger_name`.
- Operation logs record IP + request metadata; no user accounts or roles.
- For full API details, see `backend/API_REFERENCE.md`.
