# Reviewer Guide

This project is designed so an evaluator can inspect both product reasoning and engineering rigor.

## Requirement Mapping

| Exercise requirement | Where to look |
| --- | --- |
| Start endpoint | `POST /api/v1/pipeline/start` |
| Audit endpoint | `POST /api/v1/pipeline/audit/{tracking_id}` |
| Finalize loop | `POST /api/v1/pipeline/finalize/{tracking_id}` |
| Reviewer console | `GET /` |
| UI provider switch | Reviewer console supports deterministic mock, local Ollama, and API-compatible modes |
| Air-gapped LLM calls | `PipelineService` passes only current text/suggestions to the provider |
| Model declares text perfect | Audit response includes `is_perfect`, `quality_score`, and `rationale` |
| DB persistence | `pipeline_runs`, `text_versions`, `audits`, `llm_calls` |
| Prompts | `src/videoedgeai_task/llm.py` |
| Full run example | `python scripts/demo.py` |
| Metrics, baselines, and convergence | `python scripts/evaluate_metrics.py` |
| Prompt variant rationale | `python scripts/evaluate_prompt_variants.py` |
| Evaluation methodology | `docs/EVALUATION.md` |
| Committed evaluation snapshot | `docs/EVALUATION_RESULTS.md` |
| Tests | `pytest` |

## Excellent-Signal Checks

- Run `python scripts/quality_gate.py` to execute tests, lint, type checks, deterministic metrics,
  and prompt-variant evaluation.
- Start `scripts\run_reviewer_console.cmd` on Windows, then open `http://127.0.0.1:8000/` for
  the browser reviewer console.
- Use the console's provider switch to compare deterministic mock runs, free local Ollama runs,
  and OpenAI-compatible API runs. API keys entered in the UI are request-only and are not
  persisted in `llm_calls`.
- If Ollama is installed, run `ollama pull llama3.2:3b` and then
  `python scripts/ollama_smoke.py` before using the Ollama UI mode.
- Inspect `GET /api/v1/pipeline/{tracking_id}` to see versions, audits, and LLM call records.
- Inspect `GET /api/v1/pipeline/{tracking_id}/metrics` to see compact traceability metrics.
- Confirm the latest audit verdict exposes whether the fresh model call declared the text perfect.
- Inspect each `llm_calls` item for prompt version, exact request payload, provider params, model,
  input text version id, and output text version id.
- Compare `outputs/evaluation_report.md` baselines to see how raw input, fixed-template output,
  and the full pipeline differ.
- Read `docs/EVALUATION_RESULTS.md` if you want the latest committed metric snapshot without
  running the scripts.
- Compare `v0.1.0`, `v0.2.0`, and later tags to see the baseline implementation and improvement
  passes.

## Expected Behavior

- Vague ideas should usually audit as not perfect, polish once, then converge after a fresh audit.
- Already structured ideas should audit as perfect and skip polishing.
- Re-running finalize on a completed pipeline should not create extra LLM calls.
- The mock provider should produce deterministic results.
