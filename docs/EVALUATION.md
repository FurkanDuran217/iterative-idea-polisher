# Evaluation Methodology

The project has two deterministic evaluation paths:

1. `python scripts/evaluate_metrics.py`
2. `python scripts/evaluate_prompt_variants.py`

Both run without API keys. They are designed to help a reviewer inspect behavior quickly, not to
pretend that a mock provider can prove real-world writing quality.

There is also an optional local-LLM smoke path:

```bash
ollama pull llama3.2:3b
python scripts/ollama_smoke.py
```

This is intentionally not part of the required quality gate because it depends on a reviewer having
Ollama installed and running. It verifies that the same audit/polish provider interface works with
a free local model.

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
