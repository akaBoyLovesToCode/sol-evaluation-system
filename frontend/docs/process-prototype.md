# Process Builder Prototype

Primary route: `/evaluations/:id/processes/edit`
Legacy prototype alias: `/prototypes/process-builder`

## Summary

This view is now the production editor for nested processes. When opened with an evaluation ID it loads and persists data via `/evaluations/:id/processes/nested`; visiting the legacy prototype alias without an ID still seeds mock data for quick demos. Saved payloads are normalized into relational tables and also archived verbatim in `evaluation_processes_raw` as a rollback safety net.

## Payload contract

```jsonc
{
  "lot_number": "<string>",
  "quantity": <number>,
  "steps": [
    {
      "order_index": <number>,
      "step_code": "<string>",
      "step_label": "<string | optional>",
      "eval_code": "<string>",
      "total_units": <number>,
      "pass_units": <number>,
      "fail_units": <number>,
      "notes": "<string | optional>",
      "failures": [
        {
          "sequence": <number>,
          "serial_number": "<string | optional>",
          "fail_code_id": <number | optional>,
          "fail_code_text": "<string>",
          "fail_code_name_snapshot": "<string | optional>",
          "analysis_result": "<string | optional>"
        }
      ]
    }
  ]
}
```

- `order_index` and `sequence` are derived client-side to preserve submission order.
- Each step enforces a single `eval_code`.
- `fail_code_id` refers to the optional dictionary lookup; the UI still persists rows without an ID when the code is not yet curated.

## Validations implemented in the mock

- Lot number is required; whitespace is trimmed.
- Quantity must be `> 0`.
- At least one step is required.
- Each step verifies:
  - `step_code` present (normalized to uppercase).
  - `eval_code` present (normalized to uppercase).
  - `total_units === pass_units + fail_units`.
- Each failure row enforces:
  - `fail_code_text` required (normalized to uppercase).
  - Failures missing a dictionary entry are allowed but flagged with a visual chip.

## Dictionary interaction

- The fail-code field uses an autocomplete backed by mock dictionary entries. Selecting an entry sets both `fail_code_id` and `fail_code_name_snapshot`.
- Typing a code that does not exist keeps `fail_code_id = null` and surfaces a “not in dictionary” tag so maintainers can curate it later.
- The payload always includes `fail_code_text`; snapshot/name is optional.

## Copy/export helper

The payload preview panel displays the normalized JSON payload and exposes a "Copy JSON" action for quick sharing during review sessions.

## Follow-up implementation notes

- The prototype keeps additional fields (e.g., `_notInDictionary`) out of the payload normalization by trimming and rebuilding the structure before export.
- Table rendering deliberately mirrors the structure expected in the Evaluation Detail view to ease reuse when we wire the real API.
