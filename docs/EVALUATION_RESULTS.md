# Evaluation Results Snapshot

Snapshot date: 2026-06-15

Command:

```bash
python scripts/quality_gate.py
```

Result: passed.

## Quality Gate

| Check | Result |
| --- | --- |
| tests | 34 passed |
| lint | passed |
| typecheck | passed |
| deterministic metrics | passed |
| prompt variants | passed |
| air-gap case matrix | passed |

Optional Ollama smoke is available through `python scripts/ollama_smoke.py`. It is not part of the
required quality gate because it depends on a local Ollama service and a pulled model.

The current Gemini smoke is intentionally not counted as passed because the configured key returned
`429 Too Many Requests` during `python scripts/provider_smoke.py --provider gemini`. The committed
case matrix therefore uses Mock until Gemini quota or billing is available.

## Baseline Comparison

| Method | Quality | Struct | Faith | Clarity | Action | Trace | Word Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `fixed_template` | 5.00 | 1.00 | 1.00 | 5.00 | 5.00 | 0.00 | 50.00 |
| `original_input` | 2.12 | 0.12 | 1.00 | 2.25 | 0.62 | 0.00 | 0.00 |
| `pipeline_mock` | 4.94 | 1.00 | 1.00 | 4.75 | 5.00 | 5.00 | 68.88 |

The fixed-template baseline scores strongly on label-based text metrics. That is intentional: it
shows why label checks alone are not enough. The pipeline's differentiator is not only text shape;
it is the persisted audit/polish loop, prompt-versioned LLM calls, request payloads, and text-version
links that make the process inspectable.

## API Metrics

| Metric | Value |
| --- | ---: |
| case_count | 8 |
| success_rate | 1.00 |
| converged_rate | 1.00 |
| expected_polish_detection_rate | 1.00 |
| avg_iterations | 0.88 |
| avg_llm_calls | 2.75 |
| avg_total_api_ms | 107.12 |
| p95_total_api_ms | 162 |
| avg_quality_proxy_score | 4.94 |
| avg_structure_coverage | 1.00 |
| avg_faithfulness_recall | 1.00 |
| all_llm_calls_successful_rate | 1.00 |
| air_gap_trace_rate | 1.00 |
| determinism_passed | true |

## Air-Gap Case Matrix

| Metric | Value |
| --- | ---: |
| ready_or_improved_rate | 1.00 |
| completed_rate | 1.00 |
| air_gap_trace_rate | 1.00 |
| likely_better_rate | 0.88 |
| expected_polish_detection_rate | 1.00 |
| avg_iterations | 0.88 |
| avg_llm_calls | 2.75 |
| avg_quality_delta | 2.74 |
| avg_structure_coverage | 1.00 |
| avg_faithfulness_recall | 0.99 |
| avg_actionability_score | 5.00 |
| instruction_echo_count | 0 |
| non_air_gap_overclaim_count | 1 |

The non-air-gap control overclaimed improvement on the already-ready case, while the fresh
air-gapped audit correctly skipped polishing at iteration 0. The prompt-injection-like case did not
echo instruction-like text into the final output.

## Prompt Variant Results

| Type | Variant | Selected | Score | Reason |
| --- | --- | --- | ---: | --- |
| audit | `audit.loose_v0` | no | 2.25 | Too hard to parse and retry safely. |
| audit | `audit.verdict_json_v2` | yes | 4.75 | Strict JSON plus explicit perfection verdict. |
| audit | `audit.rubric_json_v2` | no | 4.00 | Useful later, but increases scope and style-churn risk. |
| polish | `polish.verbose_v0` | no | 2.50 | Explanations contaminate stored text versions. |
| polish | `polish.idea_brief_v2` | yes | 5.00 | Stores only the structured candidate text for the next audit. |
| polish | `polish.creative_v2` | no | 3.50 | More novelty, but higher faithfulness risk. |

## Representative Output

Input:

```text
make notes better for founders
```

Pipeline final output:

```text
Problem: Early-stage founders collect useful notes but struggle to turn them into a clear, reviewable next action.

Audience: Early-stage founders who turn rough notes into product decisions or pitches.

Value: The workflow turns a vague idea into a structured brief that is easier to judge, test, and improve.

Next step: Test this brief with one target user using the original idea: make notes better for founders.

Success measure: A reviewer can identify the user, problem, benefit, next step, and evaluation criterion without asking follow-up questions.
```

## Interpretation

These numbers are contract and traceability evidence, not a claim that the mock provider has human
editorial judgment. A final quality assessment should still use human review or a frozen evaluator
rubric for specificity, faithfulness, usefulness, concision, and task fit.
