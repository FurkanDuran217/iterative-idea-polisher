# Changelog

## v0.14.0 - Domain Coverage Expansion and System Performance Analysis

- Extended Mock provider domain coverage to 10 domains: founder/startup, education, healthcare,
  B2B/sales, HR/onboarding, sustainability/climate, consumer/personal, operations/postmortem,
  research/analyst, and ops — including complaint-framing and Turkish keyword detection.
- Added `scripts/analyze_system.py` — a 16-case comprehensive analysis script covering all
  extended domains, edge cases (tiny fragment, implementation-heavy, complaint framing, multilingual
  Turkish, prompt injection, multiple problems, already-ready) with per-case faithfulness,
  structure coverage, quality delta, instruction-echo, and domain-generic-fallback metrics.
- Added `docs/SYSTEM_PERFORMANCE.md` with real outputs from running the 16-case matrix: aggregate
  results, domain-by-domain breakdown, prompt engineering quality analysis, failure modes, and
  representative outputs for all eight highlighted cases.
- Added System Performance Analysis section to README summarising key findings (1.0 completion
  rate, 1.0 air-gap trace validity, 0.99 avg faithfulness, 0 instruction-echo events, 108ms avg
  latency) and linking to the full report.

## v0.13.0 - Air-Gap Prompt Engineering Analysis

- Added `scripts/evaluate_air_gap_cases.py` to run a real endpoint-level case matrix across
  vague, already-ready, underspecified, education, implementation-heavy, prompt-injection-like,
  and research-caveat inputs.
- Added `docs/AIR_GAP_ANALYSIS.md` with real final outputs, aggregate metrics, limitations, and
  an explicit air-gap vs stateful non-air-gap control.
- Hardened v6 audit/polish prompts so user-provided instruction-like text is treated as untrusted
  content and is not echoed into final briefs.
- Added the air-gap case matrix to the quality gate.
- Updated README and reviewer docs with the analysis command, example situations, real outputs,
  and Gemini quota limitation.

## v0.12.0 - Reviewer Report and Similar-System Analysis

- Added `GET /api/v1/pipeline/{tracking_id}/report` for a copyable Markdown handoff report.
- Added a Reviewer Report panel to the console so decision, score deltas, trace evidence,
  prompt versions, providers, and next checks are visible in one place.
- Added `docs/SYSTEM_ANALYSIS.md` comparing the project against LangSmith, Langfuse, promptfoo,
  and OpenAI Evals patterns.
- Added API tests for completed and not-yet-finalized report states.

## v0.11.0 - Gemini Default UX and Prompt Pass

- Added a click-to-open blue provider info button so setup guidance stays available without
  crowding the main run controls.
- Clarified the zero-click Server provider path for local Gemini defaults and request-level
  provider overrides.
- Tightened audit and polish prompts to produce shorter, reviewer-ready idea briefs with concrete
  next steps and observable success measures.
- Updated the mock provider output shape to better match the production prompt target.
- Kept deterministic evaluation pinned to Mock so local Gemini defaults do not skew baseline tests.

## v0.10.1 - Provider Help Usability

- Moved provider information out of tiny segment tooltips into the selected provider panel.
- Added actionable setup guidance for Server default, Gemini, GPT, Claude, Ollama, and Mock.
- Documented provider-specific key locations, `.env` variable names, model fields, and common
  Gemini `401`/`429` failure meanings directly in the reviewer console.
- Isolated API tests from local `.env` provider keys so reviewer machines stay deterministic.

## v0.10.0 - Gemini and Claude Provider Pass

- Added Gemini and Claude REST providers alongside Mock, Ollama, GPT/OpenAI, and
  OpenAI-compatible endpoints.
- Added server-default provider behavior: `GEMINI_API_KEY` makes Gemini the default when
  `LLM_PROVIDER` is not set; otherwise the service safely falls back to Mock.
- Expanded reviewer-console provider choices with Server, Gemini, GPT, Claude, Ollama, and Mock.
- Added provider help buttons and credential/model fields for Gemini and Claude.
- Added Gemini provider contract tests and provider-body validation tests.

## v0.9.1 - Ollama Convergence Fix

- Tightened audit and polish prompts for local LLMs so the loop does not drift into product-spec
  or implementation-detail suggestions.
- Added a high-score optional-style suggestion guard to stop local-model style churn.
- Verified a real local Ollama `llama3.2:3b` run through the FastAPI pipeline.

## v0.9.0 - Local LLM Provider

- Added an Ollama provider using `/api/chat`, non-streaming responses, and JSON mode for audits.
- Added OpenAI-compatible base URL support for local or hosted model gateways.
- Expanded the reviewer console with Mock, Ollama, and API provider controls.
- Added an optional `scripts/ollama_smoke.py` real-local-LLM check.
- Added tests for Ollama provider selection and request payload shape.

## v0.8.0 - Provider Selection UI

- Added request-level provider overrides for audit and finalize endpoints.
- Added reviewer-console controls for deterministic mock mode and per-request OpenAI mode.
- Kept OpenAI API keys out of persisted request payloads and trace records.
- Added API tests for provider override behavior and missing OpenAI key validation.

## v0.7.0 - Smart Verdict Pipeline

- Upgraded audit prompts to return explicit `is_perfect`, `quality_score`, `rationale`, and
  `suggestions` fields.
- Updated finalize behavior to stop when a fresh audit call declares the text perfect.
- Improved mock provider behavior with clearer audience/problem/value inference for offline demos.
- Added latest audit verdict fields to the metrics endpoint and reviewer UI.
- Reframed the UI around the actual air-gapped loop: fresh audit verdict, polish result, metrics,
  and trace timeline.

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
