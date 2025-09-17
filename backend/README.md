# Backend API Service (Simplified, Auth‑less)

Flask + SQLAlchemy + MySQL backend for the Evaluation Manager. This simplified variant removes users/roles/auth and focuses on public, easy‑to‑use evaluation APIs with IP‑based operation logging.

## Stack
- Flask, Flask‑SQLAlchemy, Flask‑Migrate, Flask‑CORS
- MySQL 8 (PyMySQL)
- uv for Python dependency/runtime management

## Key Changes
- No authentication or roles (JWT removed).
- No users/messages/notifications/workflow/dashboard modules.
- Chargers are free‑text fields: `scs_charger_name`, `head_office_charger_name`.
- Operation logs record IP/user‑agent and request metadata (method, path, query, status).

## Requirements
- Python 3.13+
- MySQL 8.0+
- uv installed (`pipx install uv` or refer to uv docs)

## Setup
1) Install deps
```bash
cd backend
uv pip sync requirements.txt
```

2) Configure env (`.env`)
```env
SECRET_KEY=dev-secret-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=evaluation
FLASK_ENV=development
```

3) Migrate + init
```bash
flask db upgrade
flask init-db
```

4) Run
```bash
python run.py
# or
flask run --host=0.0.0.0 --port=5001
```

Base URL: `http://localhost:5001`

## API Overview (Public, No Auth)
- GET `/api/evaluations` – List evaluations
  - Filters: `status`, `evaluation_type`, `product_name`, `scs_charger_name`, `head_office_charger_name`, `page`, `per_page`
- GET `/api/evaluations/{id}` – Get evaluation details (includes processes and logs)
- POST `/api/evaluations` – Create evaluation (auto‑generates `evaluation_number` if omitted)
- PUT `/api/evaluations/{id}` – Update evaluation
- DELETE `/api/evaluations/{id}` – Delete evaluation
- GET `/api/evaluations/{id}/processes` – List processes
- POST `/api/evaluations/{id}/processes` – Create process
- GET `/api/evaluations/{id}/processes/{process_id}` – Get process
- PUT `/api/evaluations/{id}/processes/{process_id}` – Update process
- DELETE `/api/evaluations/{id}/processes/{process_id}` – Delete process
- PUT `/api/evaluations/{id}/status` – Update status (reserved statuses accepted; approvals not enforced)
- GET `/api/evaluations/{id}/logs` – List operation logs

Notes
- Statuses retained: `draft`, `in_progress`, `pending_part_approval`, `pending_group_approval`, `completed`, `paused`, `cancelled`, `rejected` (no role checks).
- Logs include: `ip_address`, `user_agent`, `request_method`, `request_path`, `query_string`, `status_code`.
- Chargers are captured as plain text names.

## Data Model (key fields)
- evaluations
  - id, evaluation_number, evaluation_type, product_name, part_number, status
  - start_date, actual_end_date, process_step, evaluation_reason
  - scs_charger_name, head_office_charger_name
  - created_at, updated_at
- evaluation_processes
  - id, evaluation_id, eval_code, lot_number, quantity, process_description,
    manufacturing_test_results, defect_analysis_results, aql_result, status,
    created_at, updated_at
- operation_logs
  - id, operation_type, target_type, target_id, operation_description,
    old_data, new_data, ip_address, user_agent, request_method,
    request_path, query_string, status_code, success, error_message, created_at

## Project Structure (trimmed)
```
backend/
  app/
    __init__.py
    api/
      __init__.py
      evaluation.py
    models/
      __init__.py
      evaluation.py
      operation_log.py
      system_config.py
    services/
      __init__.py
      backup_service.py
    utils/
      __init__.py
      helpers.py
      validators.py
  migrations/
  run.py
  requirements.txt
  pyproject.toml
```

## Migrations
- Alembic migration `ee9a7b3f3b9a` drops user FKs/columns and adds name fields + request metadata to logs.
- Apply with `flask db upgrade`.

## Testing
- Auth/user tests removed. Focus on evaluation, processes, and logging.
- If configured: `PYTHONPATH=. uv run pytest`.

