# Changelog

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

