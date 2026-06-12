# Reviewer Guide

This project is designed so an evaluator can inspect both product reasoning and engineering rigor.

## Requirement Mapping

| Exercise requirement | Where to look |
| --- | --- |
| Start endpoint | `POST /api/v1/pipeline/start` |
| Audit endpoint | `POST /api/v1/pipeline/audit/{tracking_id}` |
| Finalize loop | `POST /api/v1/pipeline/finalize/{tracking_id}` |
| Air-gapped LLM calls | `PipelineService` passes only current text/suggestions to the provider |
| DB persistence | `pipeline_runs`, `text_versions`, `audits`, `llm_calls` |
| Prompts | `src/videoedgeai_task/llm.py` |
| Full run example | `python scripts/demo.py` |
| Metrics and convergence | `python scripts/evaluate_metrics.py` |
| Tests | `pytest` |

## Excellent-Signal Checks

- Run `python scripts/quality_gate.py` to execute tests, lint, type checks, and deterministic metrics.
- Inspect `GET /api/v1/pipeline/{tracking_id}` to see versions, audits, and LLM call records.
- Inspect `GET /api/v1/pipeline/{tracking_id}/metrics` to see compact traceability metrics.
- Inspect each `llm_calls` item for prompt version, exact request payload, provider params, model,
  input text version id, and output text version id.
- Compare `v0.1.0` and `v0.2.0` to see the baseline implementation and the excellence pass.

## Expected Behavior

- Vague ideas should usually polish once, then converge.
- Already structured ideas should audit cleanly and skip polishing.
- Re-running finalize on a completed pipeline should not create extra LLM calls.
- The mock provider should produce deterministic results.
