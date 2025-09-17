# API Quick Reference (Auth‑less)

## Base URL
- Development: `http://localhost:5001`

## Evaluations

- GET `/api/evaluations`
  - Query: `page`, `per_page`, `status`, `evaluation_type`, `product_name`, `scs_charger_name`, `head_office_charger_name`
  - 200: `{ success, data: { evaluations: [...], total, page, per_page, pages } }`

- GET `/api/evaluations/{id}`
  - 200: `{ success, data: { evaluation: { ... , processes, logs } } }`

- POST `/api/evaluations`
  - Body (required): `evaluation_type`, `product_name`, `part_number`, `start_date`, `process_step`
  - Body (optional): `evaluation_number`, `evaluation_reason`, `remarks|description`, `pgm_version`, `capacity`, `interface_type`, `form_factor`, `scs_charger_name`, `head_office_charger_name`, `status`
  - 201: `{ success, message, data: { evaluation } }`

- PUT `/api/evaluations/{id}`
  - Body: any editable field from above
  - 200: `{ success, message, data: { evaluation } }`

- DELETE `/api/evaluations/{id}`
  - 200: `{ success, message }`

## Processes

- GET `/api/evaluations/{id}/processes`
  - 200: `{ success, data: { processes: [...] } }`

- POST `/api/evaluations/{id}/processes`
  - Body (required): `eval_code`, `lot_number`, `quantity`, `process_description`
  - Optional: `title`, `manufacturing_test_results`, `defect_analysis_results`, `aql_result`
  - 201: `{ success, message, data: { process } }`

- GET `/api/evaluations/{id}/processes/{process_id}`
  - 200: `{ success, data: { process } }`

- PUT `/api/evaluations/{id}/processes/{process_id}`
  - Body: any editable field from POST
  - 200: `{ success, message, data: { process } }`

- DELETE `/api/evaluations/{id}/processes/{process_id}`
  - 200: `{ success, message }`

## Status

- PUT `/api/evaluations/{id}/status`
  - Body: `{ status: 'draft' | 'in_progress' | 'pending_part_approval' | 'pending_group_approval' | 'completed' | 'paused' | 'cancelled' | 'rejected' }`
  - 200: `{ success, message, data: { evaluation } }`

## Logs

- GET `/api/evaluations/{id}/logs`
  - 200: `{ success, data: { logs: [{ id, operation_type, target_type, operation_description, ip_address, user_agent, request_method, request_path, query_string, status_code, created_at, ... }] } }`

## Notes
- No Authorization header; all endpoints are public.
- Chargers are free text: `scs_charger_name`, `head_office_charger_name`.
- Operation logs are IP‑based and include request metadata.

