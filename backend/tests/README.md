# Backend Test Suite Notes

## Scope
- Unit coverage focuses on the evaluation domain: app factory wiring, `Evaluation`, `EvaluationProcess`, and `OperationLog`.
- Authentication/JWT flows and user models are **not** part of the backend codebase and are no longer referenced in tests.
- Integration scripts live under `tests/integration/`; they expect external services and may rely on optional dependencies such as `requests`.

## Recent Changes
- Removed JWT Extended fixtures and token helpers that pulled in an unused dependency.
- Deleted user-model tests and helpers that referenced non-existent backend tables.
- Normalised shared helpers to work without user IDs (`tests/helpers.py`).
- Guarded integration imports with `pytest.importorskip` so unit runs stay lightweight.

## Running Tests
```bash
# Full suite (unit tests only at the moment)
uv run pytest

# Unit layer explicitly
uv run pytest -m unit

# Single file example
uv run pytest tests/unit/test_evaluation_processes.py -v
```

## Known Warnings
- `SAWarning: configure() can not affect sessions that have already been created` appears when the scoped session fixture rebinds the engine. This is benign for in-memory SQLite but worth revisiting if fixtures are refactored.
- Integration tests still assume external services; mark them or skip when the API stack is unavailable.

## Maintenance Tips
- Keep unit specs aligned with the actual SQLAlchemy models under `app/models`.
- Avoid reintroducing JWT or user fixtures unless the backend regains those features.
- When adding integration tests, wrap third-party imports with `pytest.importorskip` to keep core suites dependency-free.

_Last updated: 2025-09-26_
