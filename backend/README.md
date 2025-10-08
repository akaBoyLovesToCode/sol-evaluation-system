# Backend API Service (Simplified, Auth‑less)

Flask + SQLAlchemy + MySQL backend for the Evaluation Manager. This simplified variant removes users/roles/auth and focuses on public, easy‑to‑use evaluation APIs with IP‑based operation logging.

## Stack
- Flask, Flask‑SQLAlchemy, Flask‑Migrate, Flask‑CORS
- MySQL 8 (PyMySQL)
- uv for Python dependency/runtime management

## Key Changes
- No authentication or roles (JWT removed).
- No users/messages/notifications/workflow/dashboard modules.
- Chargers are free-text fields: `scs_charger_name`, `head_office_charger_name`.
- Operation logs record IP/user-agent and request metadata (method, path, query, status).
- `/api/evaluations/:id/processes/nested` is always enabled and now persists multi-lot nested
  processes with optional totals per step.

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
    created_at, updated_at (legacy free-form records; still readable)
- evaluation_processes_raw
  - id, evaluation_id, payload (full JSON), source, created_at, updated_at
- evaluation_process_lots
  - id, evaluation_id, lot_number, quantity, created_at, updated_at
- evaluation_process_steps
  - id, evaluation_id, lot_number (legacy aggregate label), quantity (legacy sum),
    order_index, step_code, step_label, eval_code (nullable), results_applicable,
    total_units (nullable), total_units_manual, pass_units (nullable),
    fail_units (nullable), notes, created_at, updated_at
- evaluation_step_lots
  - step_id, lot_id, quantity_override (reserved), created_at, updated_at
- evaluation_step_failures
  - id, step_id, sequence, serial_number, fail_code_id, fail_code_text,
    fail_code_name_snapshot, analysis_result, created_at, updated_at
- fail_codes
  - id, code (unique), short_name, description, created_at, updated_at
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
- `ee9a7b3f3b9a`: drops user FKs/columns and adds name fields + request metadata to logs.
- `e8a1d6b1f2c3`: introduces the original nested process tables (raw payload + step/failure rows).
- `5f8c7d9e3b10`: adds multi-lot support (`evaluation_process_lots`, `evaluation_step_lots`) and
  relaxes step columns (`eval_code` optional, totals nullable, `results_applicable`,
  `total_units_manual`).

Run migrations via uv to ensure the managed virtualenv is used:

```bash
cd backend
uv run flask db upgrade
# to verify reversibility during development
uv run flask db downgrade e8a1d6b1f2c3
uv run flask db upgrade
```

## Testing
- Auth/user tests removed. Focus on evaluation, processes, and logging.
- If configured: `PYTHONPATH=. uv run pytest`.

## Fail-code dictionary bootstrap

Use the helper script to seed/update the fail-code dictionary from CSV/XLSX datasets:

```bash
cd backend
python -m scripts.bootstrap_fail_codes \
  --code-column fail_code \
  --name-column fail_name \
  data/historical/fails/*.xlsx
```

Outputs (written to `reports/fail_code_bootstrap/` by default):
- `missing_names.csv` – codes lacking names for curation.
- `conflicts.csv` – codes with differing names across inputs.
- `errors.csv` – problematic rows that were skipped (e.g., missing code).
- `ingestion_log.json` – summary metrics per file and total rows affected.

Use `--description-column` when legacy sheets include a longer explanation, and `--use-description` to populate the `description` column when available.
All nested-process saves also archive the raw JSON payload in `evaluation_processes_raw`, providing a rollback safety net if structured inserts ever need to be replayed.

### Text extraction mode

When historical data mixes codes and descriptions inside free text (e.g., `评价过程`), switch to the new text-mining workflow:

```bash
python -m scripts.bootstrap_fail_codes \
  --mode text-extract \
  --text-col "评价过程" \
  --text-col "评价描述" \
  --stopwords-file ./stopwords.txt \
  --deny-regex "^M\\d{3}$" --deny-regex "^R\\d{3}$" \
  data/historical/*.xlsx --out-dir reports/text_extract
```

This mode:
- mines numeric/acronym tokens (`code_regexes`) and Chinese failure phrases,
- filters obvious non-codes using stopwords + deny regexes,
- assigns provisional codes (e.g., `LEGACY-*`) when only a failure name is found,
- records raw hits, distinct token rollups, alias mappings, and ingestion metrics.

Review `distinct_tokens.csv`, merge aliases into canonical codes, and re-run as needed. You can supply extra patterns/stopwords via a YAML config file passed to `--config` if the defaults in the script need adjustment.
