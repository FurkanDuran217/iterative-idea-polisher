# Reviewer Guide

This project is designed so an evaluator can inspect both product reasoning and engineering rigor.

## Requirement Mapping

| Exercise requirement | Where to look |
| --- | --- |
| Start endpoint | `POST /api/v1/pipeline/start` |
| Audit endpoint | `POST /api/v1/pipeline/audit/{tracking_id}` |
| Finalize loop | `POST /api/v1/pipeline/finalize/{tracking_id}` |
| Reviewer console | `GET /` |
| UI provider switch | Reviewer console supports Server, Gemini, GPT, Claude, Ollama, and Mock modes |
| Provider setup help | Blue `i` button in the reviewer console provider card |
| Air-gapped LLM calls | `PipelineService` passes only current text/suggestions to the provider |
| Model declares text perfect | Audit response includes `is_perfect`, `quality_score`, and `rationale` |
| DB persistence | `pipeline_runs`, `text_versions`, `audits`, `llm_calls` |
| Prompts | `src/videoedgeai_task/llm.py` |
| Full run example | `python scripts/demo.py` |
| Metrics, baselines, and convergence | `python scripts/evaluate_metrics.py` |
| Original-vs-final review API | `GET /api/v1/pipeline/{tracking_id}/review` |
| Reviewer handoff report | `GET /api/v1/pipeline/{tracking_id}/report` |
| Similar-system analysis | `docs/SYSTEM_ANALYSIS.md` |
| Prompt variant rationale | `python scripts/evaluate_prompt_variants.py` |
| Air-gap prompt analysis | `python scripts/evaluate_air_gap_cases.py --write-docs` |
| Evaluation methodology | `docs/EVALUATION.md` |
| Committed evaluation snapshot | `docs/EVALUATION_RESULTS.md` |
| Committed air-gap analysis | `docs/AIR_GAP_ANALYSIS.md` |
| Tests | `pytest` |

## Excellent-Signal Checks

- Run `python scripts/quality_gate.py` to execute tests, lint, type checks, deterministic metrics,
  prompt-variant evaluation, and the air-gap case matrix.
- Start `scripts\run_reviewer_console.cmd` on Windows, then open `http://127.0.0.1:8000/` for
  the browser reviewer console.
- Use the console's provider switch to compare deterministic mock runs, free local Ollama runs,
  Gemini/GPT/Claude API runs, and server-default behavior. API keys entered in the UI are
  request-only and are not persisted in `llm_calls`.
- Use the blue `i` button next to `LLM Provider` for provider-specific setup steps and key
  locations. Server mode should be the zero-click path when `GEMINI_API_KEY` is configured.
- If Ollama is installed, run `ollama pull llama3.2:3b` and then
  `python scripts/ollama_smoke.py` before using the Ollama UI mode.
- Inspect `GET /api/v1/pipeline/{tracking_id}` to see versions, audits, and LLM call records.
- Inspect `GET /api/v1/pipeline/{tracking_id}/metrics` to see compact traceability metrics.
- Inspect `GET /api/v1/pipeline/{tracking_id}/review` to compare original and current text with
  structure, faithfulness, clarity, actionability, and quality proxy scores.
- Inspect `GET /api/v1/pipeline/{tracking_id}/report` for a copyable handoff report that combines
  decision, score deltas, trace evidence, prompt versions, providers, and next checks.
- Confirm the latest audit verdict exposes whether the fresh model call declared the text perfect.
- Inspect each `llm_calls` item for prompt version, exact request payload, provider params, model,
  input text version id, and output text version id.
- Compare `outputs/evaluation_report.md` baselines to see how raw input, fixed-template output,
  and the full pipeline differ.
- Read `docs/AIR_GAP_ANALYSIS.md` to inspect the real endpoint outputs for vague, already-ready,
  underspecified, education, implementation-heavy, prompt-injection-like, and research-caveat
  cases.
- Read `docs/EVALUATION_RESULTS.md` if you want the latest committed metric snapshot without
  running the scripts.
- Compare `v0.1.0`, `v0.2.0`, and later tags to see the baseline implementation and improvement
  passes.

## Expected Behavior

- Vague ideas should usually audit as not perfect, polish once, then converge after a fresh audit.
- Already structured ideas should audit as perfect and skip polishing.
- Re-running finalize on a completed pipeline should not create extra LLM calls.
- The mock provider should produce deterministic results.
