# Evaluation Methodology

The project has four deterministic evaluation paths:

1. `python scripts/evaluate_metrics.py`
2. `python scripts/evaluate_prompt_variants.py`
3. `python scripts/evaluate_air_gap_cases.py --write-docs`
4. `python scripts/analyze_system.py --write-docs`

All three run without API keys by default. They are designed to help a reviewer inspect behavior quickly, not to
pretend that a mock provider can prove real-world writing quality.

For a single live run, `GET /api/v1/pipeline/{tracking_id}/review` exposes the same style of
deterministic original-vs-current comparison through the API. Use that endpoint after `finalize`
when you want a compact answer to whether the pipeline probably improved the submitted idea.

There is also an optional local-LLM smoke path:

```bash
ollama pull llama3.2:3b
python scripts/ollama_smoke.py
```

This is intentionally not part of the required quality gate because it depends on a reviewer having
Ollama installed and running. It verifies that the same audit/polish provider interface works with
a free local model.

## System Performance Analysis

`scripts/analyze_system.py --write-docs` writes:

- `outputs/system_analysis.json`
- `outputs/system_analysis_report.md`
- `docs/SYSTEM_PERFORMANCE.md`

The script runs 16 cases across 15 domain categories: founder (2 variants), education, healthcare,
B2B/sales, HR/onboarding, sustainability, operations, research, underspecified fragment, over-specified
implementation-heavy, complaint framing, multilingual Turkish, adversarial injection, complex scope,
and already-ready stop condition. For each case it records:

- `iteration_count` and `llm_call_count`
- `air_gap_trace_ok`
- `structure_coverage`: fraction of required labels present in the final output
- `faithfulness_recall`: content-word overlap between original and final text
- `quality_delta`: score improvement from original to final
- `instruction_echo`: whether instruction-like user text appeared in the output
- `domain_generic_fallback`: whether the mock provider fell back to a generic audience line

The committed `docs/SYSTEM_PERFORMANCE.md` uses Mock for reproducibility. A live-LLM run can be
produced by setting `LLM_PROVIDER=gemini` (or any other provider) before running the script.

## Air-Gap Case Matrix

`scripts/evaluate_air_gap_cases.py --write-docs` writes:

- `outputs/air_gap_analysis.json`
- `outputs/air_gap_analysis_report.md`
- `docs/AIR_GAP_ANALYSIS.md`

The matrix actually runs the FastAPI app through the start, audit, finalize, detail, metrics,
review, and report endpoints for each case. It covers vague input, already-ready input, messy
customer research, a tiny fragment, an education workflow, implementation-heavy input,
prompt-injection-like user text, and research-caveat preservation.

The committed snapshot uses Mock for reproducibility. It can be rerun on Gemini with:

```bash
python scripts/evaluate_air_gap_cases.py --provider gemini --write-docs
```

Gemini results should only be committed after the configured key is quota-ready. Until then, the
Mock matrix is evidence for pipeline behavior, prompt guardrails, traceability, and deterministic
non-air-gap overclaim detection, not a claim of live Gemini writing quality.

## Metrics

`scripts/evaluate_metrics.py` writes:

- `outputs/evaluation_metrics.json`
- `outputs/evaluation_report.md`

The report compares the API pipeline against two baselines:

- `original_input`: no rewrite. This shows how far the raw text already gets.
- `fixed_template`: rule-based label formatting without audit, iteration, or LLM trace records.
- `pipeline_mock`: the full FastAPI flow with start, audit, finalize, persistence, and LLM-call logs.

The metrics are intentionally transparent:

- `structure_coverage`: fraction of required labels present.
- `faithfulness_recall`: original content words preserved in the final text.
- `clarity_proxy_score`: reviewable length and paragraph structure.
- `actionability_score`: presence of next step and success measure.
- `quality_proxy_score`: average of the above signals after scaling structure and faithfulness.
- `air_gap_trace_rate`: whether LLM calls carry hashes, prompt versions, request payloads, and text
  version links.
- `traceability_score`: baseline-only engineering signal that separates text quality proxies from
  whether a method creates auditable pipeline history.

## What The Metrics Do Not Prove

These are proxy metrics. The deterministic mock provider can satisfy label-based checks easily, so
the report should be read as an engineering contract test: the loop works, traces are stored, and
outputs can be compared. It does not prove that a live model's rewrite is more original, more
persuasive, or better aligned with a hiring team's taste.

A production-quality evaluation would add human review and LLM-judge sampling with a frozen rubric:

- Specificity: can the reviewer identify user, problem, value, next action, and success criterion?
- Faithfulness: did the rewrite preserve the original intent?
- Usefulness: does the final text support a decision or experiment?
- Concision: did the system improve the idea without padding?
- Task fit: does the output match the expected hiring exercise behavior?

## Prompt Variants

`scripts/evaluate_prompt_variants.py` writes:

- `outputs/prompt_variant_evaluation.json`
- `outputs/prompt_variant_report.md`

The selected prompt pair is:

- `audit.verdict_json_v2`
- `polish.idea_brief_v2`

This pair is selected because it keeps the API contract simple:

- audits explicitly say whether the text is perfect;
- audits are easy to parse and retry;
- polish outputs do not contaminate text versions with explanations;
- each air-gapped call can be stored with a prompt version and exact request payload.

Rejected alternatives are still documented. For example, rubric-based audit prompts are attractive
for deeper evaluation, but they add scope and can keep generating new style critiques after the core
structure is already fixed.
