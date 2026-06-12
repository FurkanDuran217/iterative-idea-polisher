# Changelog

## v0.6.2 - Reviewer Console Usability Pass

- Reworked the reviewer console around a clearer three-step workflow.
- Moved the polished text and audit suggestions into the primary view.
- Added a one-click full pipeline action and cleaner metrics/trace presentation.
- Removed confusing raw-state-first layout and mojibake separator characters.

## v0.6.1 - Windows Reviewer Console Launch Fix

- Added `scripts/run_reviewer_console.ps1` and `scripts/run_reviewer_console.cmd`.
- Documented the safer Windows launch path so the UI starts from the repo root with the correct
  `src/` package path.

## v0.6.0 - Reviewer Console UI

- Added a no-dependency reviewer console at `/` for start, audit, finalize, refresh, and trace
  inspection.
- Added UI coverage in the API test suite.
- Documented the browser-based review path in README and reviewer guide.

## v0.5.0 - Baseline Evaluation and Prompt Experiments

- Expanded the deterministic evaluation report with metric definitions, limitations, baseline
  comparison, and before/after output samples.
- Added `original_input`, `fixed_template`, and `pipeline_mock` baseline comparisons.
- Added an offline prompt-variant evaluation that explains why strict audit JSON and
  final-text-only polish prompts were selected.
- Added evaluation methodology documentation for reviewer-friendly interpretation of the metrics.

## v0.4.0 - Traceability and Failure Hardening

- Added exact LLM request payload, prompt version, model name, provider params, and text-version links to `llm_calls`.
- Records failed audit/polish provider exceptions and empty polish outputs instead of losing the trace.
- Hardened audit JSON parsing for fenced JSON, duplicate suggestions, and oversized suggestion lists.
- Expanded tests for parser edge cases, failed polish calls, and trace metadata.

## v0.3.0 - VideoEdgeAI-Task Rename

- Renamed the project, package, runtime entrypoints, database defaults, and docs to `VideoEdgeAI-Task`.
- Renamed the Python package from `idea_polisher` to `videoedgeai_task`.
- Preserved the same API behavior and quality gate after the rename.

## v0.2.0 - Excellence Pass

- Added per-run metrics endpoint for reviewer/debug visibility.
- Added CI workflow for tests, lint, type checks, and deterministic metrics.
- Added reviewer guide and architecture decision notes.
- Added a single-command quality gate script.
- Added idempotency and metrics tests.

## v0.1.0 - Baseline Evaluated Implementation

- Added async FastAPI pipeline with start, audit, finalize, detail, and health endpoints.
- Added async SQLAlchemy persistence for runs, text versions, audits, and LLM calls.
- Added mock and optional OpenAI LLM providers.
- Added deterministic demo and multi-metric evaluation script.
- Added Docker, compose, Makefile, README, tests, lint, and type-check setup.
