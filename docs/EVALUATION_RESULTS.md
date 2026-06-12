# Evaluation Results Snapshot

Snapshot date: 2026-06-12

Command:

```bash
python scripts/quality_gate.py
```

Result: passed.

## Quality Gate

| Check | Result |
| --- | --- |
| tests | 17 passed |
| lint | passed |
| typecheck | passed |
| deterministic metrics | passed |
| prompt variants | passed |

## Baseline Comparison

| Method | Quality | Struct | Faith | Clarity | Action | Trace | Word Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `original_input` | 2.12 | 0.12 | 1.00 | 2.25 | 0.62 | 0.00 | 0.00 |
| `fixed_template` | 5.00 | 1.00 | 1.00 | 5.00 | 5.00 | 0.00 | 50.00 |
| `pipeline_mock` | 4.94 | 1.00 | 1.00 | 4.75 | 5.00 | 5.00 | 76.12 |

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
| avg_quality_proxy_score | 4.94 |
| avg_structure_coverage | 1.00 |
| avg_faithfulness_recall | 1.00 |
| all_llm_calls_successful_rate | 1.00 |
| air_gap_trace_rate | 1.00 |
| determinism_passed | true |

## Prompt Variant Results

| Type | Variant | Selected | Score | Reason |
| --- | --- | --- | ---: | --- |
| audit | `audit.loose_v0` | no | 2.25 | Too hard to parse and retry safely. |
| audit | `audit.strict_json_v1` | yes | 4.50 | Strict JSON makes validation and storage reliable. |
| audit | `audit.rubric_json_v2` | no | 4.00 | Useful later, but increases scope and style-churn risk. |
| polish | `polish.verbose_v0` | no | 2.50 | Explanations contaminate stored text versions. |
| polish | `polish.final_text_only_v1` | yes | 4.75 | Stores only the candidate text for the next audit. |
| polish | `polish.creative_v2` | no | 3.50 | More novelty, but higher faithfulness risk. |

## Representative Output

Input:

```text
make notes better for founders
```

Pipeline final output:

```text
Polished idea

Problem: make notes better for founders

Audience: The people or team who feel this problem directly and need a clearer way to act on the idea.

Value: The idea is easier to evaluate because it states the problem, the intended audience, the practical benefit, and the next decision point.

Next step: Test the idea with one realistic user scenario, then revise the wording based on what felt unclear or unsupported.

Success measure: A reviewer can identify the user, problem, benefit, next step, and evaluation criterion without asking follow-up questions.
```

## Interpretation

These numbers are contract and traceability evidence, not a claim that the mock provider has human
editorial judgment. A final quality assessment should still use human review or a frozen evaluator
rubric for specificity, faithfulness, usefulness, concision, and task fit.
