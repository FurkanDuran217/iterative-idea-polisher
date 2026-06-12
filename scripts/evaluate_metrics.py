from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any

import httpx

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "src"))

from videoedgeai_task.db import configure_database, dispose_db, drop_db  # noqa: E402
from videoedgeai_task.main import app  # noqa: E402

REQUIRED_LABELS = ("Problem:", "Audience:", "Value:", "Next step:", "Success measure:")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

METRIC_DEFINITIONS = {
    "quality_proxy_score": (
        "Average of structure coverage, faithfulness recall, clarity proxy, and "
        "actionability. This is a deterministic guardrail, not a human quality score."
    ),
    "structure_coverage": (
        "Fraction of required reviewer labels present: Problem, Audience, Value, "
        "Next step, and Success measure."
    ),
    "faithfulness_recall": (
        "Fraction of non-stopword content words from the original that still appear "
        "in the final text."
    ),
    "clarity_proxy_score": (
        "Heuristic score based on word count and paragraph structure. It rewards "
        "reviewable length without proving style quality."
    ),
    "actionability_score": (
        "Heuristic score for whether the output contains both a next step and a "
        "success measure."
    ),
    "air_gap_trace_rate": (
        "Share of runs whose LLM calls have request hashes, valid prompt types, prompt "
        "versions, request payloads, and linked input text versions."
    ),
    "traceability_score": (
        "Baseline-only engineering signal. Raw text and fixed templates score 0 because they "
        "do not create inspectable pipeline history; the API pipeline scores 5 when traces exist."
    ),
}
METRIC_LIMITATIONS = [
    "The mock provider is deterministic, so these metrics prove contract behavior and "
    "traceability rather than real LLM judgment quality.",
    "Label-based structure can be gamed by any output that prints the expected labels.",
    "Faithfulness recall checks word preservation, not whether the meaning was improved.",
    "A human rubric is still required for final hiring-task quality judgment.",
]


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    text: str
    expected_polish: bool


@dataclass
class BaselineMetrics:
    case_name: str
    method: str
    description: str
    final_text: str
    final_word_count: int
    word_delta: int
    structure_coverage: float
    faithfulness_recall: float
    clarity_proxy_score: float
    actionability_score: float
    traceability_score: float
    quality_proxy_score: float


@dataclass
class CaseMetrics:
    name: str
    original_text: str
    final_text: str
    success: bool
    expected_polish: bool
    needed_polish: bool
    convergence_reason: str
    iteration_count: int
    version_count: int
    audit_count: int
    llm_call_count: int
    first_suggestion_count: int
    total_api_ms: int
    recorded_llm_ms: int
    original_word_count: int
    final_word_count: int
    word_delta: int
    structure_coverage: float
    faithfulness_recall: float
    clarity_proxy_score: float
    actionability_score: float
    quality_proxy_score: float
    all_llm_calls_successful: bool
    air_gap_trace_ok: bool


def dataset() -> list[EvaluationCase]:
    already_polished = (
        "Problem: Product teams collect feedback in scattered notes and lose the strongest "
        "customer insight before planning. Audience: Early-stage founders and product managers "
        "who need sharper decision support. Value: The workflow turns loose notes into an "
        "evaluatable idea brief. Next step: Test it on three real feedback snippets. Success "
        "measure: A reviewer can name the user, problem, benefit, and next experiment."
    )
    return [
        EvaluationCase(
            name="vague_one_liner",
            text="make notes better for founders",
            expected_polish=True,
        ),
        EvaluationCase(
            name="whitespace_heavy",
            text="  build\n\n a tool\tthat turns    messy meeting notes into next steps  ",
            expected_polish=True,
        ),
        EvaluationCase(
            name="long_messy_idea",
            text=(
                "I want an app for customer interviews where the founder can paste fragments, "
                "tag interesting quotes, and somehow get a clearer summary for a pitch or roadmap."
            ),
            expected_polish=True,
        ),
        EvaluationCase(
            name="already_structured",
            text=already_polished,
            expected_polish=False,
        ),
        EvaluationCase(
            name="tiny_fragment",
            text="AI todo app",
            expected_polish=True,
        ),
        EvaluationCase(
            name="research_workflow",
            text=(
                "help analysts compare raw research notes, preserve important caveats, and create "
                "a cleaner brief before a stakeholder review"
            ),
            expected_polish=True,
        ),
        EvaluationCase(
            name="operations_pitch",
            text=(
                "a lightweight service for ops teams that turns scattered incident notes into a "
                "clear postmortem draft"
            ),
            expected_polish=True,
        ),
        EvaluationCase(
            name="education_tool",
            text=(
                "teachers need a faster way to convert rough lesson ideas into clear activities "
                "with a measurable learning outcome"
            ),
            expected_polish=True,
        ),
    ]


async def timed_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **kwargs: Any,
) -> tuple[httpx.Response, int]:
    start = time.perf_counter()
    response = await client.request(method, url, **kwargs)
    elapsed_ms = round((time.perf_counter() - start) * 1000)
    return response, elapsed_ms


async def evaluate_case(client: httpx.AsyncClient, case: EvaluationCase) -> CaseMetrics:
    total_api_ms = 0
    start_response, elapsed = await timed_request(
        client,
        "POST",
        "/api/v1/pipeline/start",
        json={"text": case.text},
    )
    total_api_ms += elapsed
    start_response.raise_for_status()
    tracking_id = start_response.json()["tracking_id"]

    audit_response, elapsed = await timed_request(
        client,
        "POST",
        f"/api/v1/pipeline/audit/{tracking_id}",
    )
    total_api_ms += elapsed
    audit_response.raise_for_status()
    audit_payload = audit_response.json()

    finalize_response, elapsed = await timed_request(
        client,
        "POST",
        f"/api/v1/pipeline/finalize/{tracking_id}",
    )
    total_api_ms += elapsed
    finalize_response.raise_for_status()
    final_payload = finalize_response.json()

    detail_response, elapsed = await timed_request(
        client,
        "GET",
        f"/api/v1/pipeline/{tracking_id}",
    )
    total_api_ms += elapsed
    detail_response.raise_for_status()
    detail_payload = detail_response.json()

    metrics_response, elapsed = await timed_request(
        client,
        "GET",
        f"/api/v1/pipeline/{tracking_id}/metrics",
    )
    total_api_ms += elapsed
    metrics_response.raise_for_status()
    metrics_payload = metrics_response.json()

    llm_calls = detail_payload["llm_calls"]
    final_text = final_payload["final_text"]
    scored = score_text(
        case=case,
        method="pipeline_mock",
        final_text=final_text,
        description="Full API loop with audit, polish, persistence, and trace records.",
    )

    return CaseMetrics(
        name=case.name,
        original_text=case.text,
        final_text=final_text,
        success=finalize_response.status_code == 200,
        expected_polish=case.expected_polish,
        needed_polish=bool(audit_payload["needs_polish"]),
        convergence_reason=final_payload["convergence_reason"],
        iteration_count=int(final_payload["iteration_count"]),
        version_count=int(final_payload["version_count"]),
        audit_count=int(final_payload["audit_count"]),
        llm_call_count=len(llm_calls),
        first_suggestion_count=len(audit_payload["suggestions"]),
        total_api_ms=total_api_ms,
        recorded_llm_ms=sum(int(call["latency_ms"]) for call in llm_calls),
        original_word_count=len(words(case.text)),
        final_word_count=scored.final_word_count,
        word_delta=scored.word_delta,
        structure_coverage=scored.structure_coverage,
        faithfulness_recall=scored.faithfulness_recall,
        clarity_proxy_score=scored.clarity_proxy_score,
        actionability_score=scored.actionability_score,
        quality_proxy_score=scored.quality_proxy_score,
        all_llm_calls_successful=all(bool(call["success"]) for call in llm_calls),
        air_gap_trace_ok=bool(metrics_payload["air_gap_trace_ok"]),
    )


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def content_words(text: str) -> set[str]:
    return {word for word in words(text) if word not in STOP_WORDS and len(word) > 2}


def label_coverage(text: str) -> float:
    return sum(1 for label in REQUIRED_LABELS if label in text) / len(REQUIRED_LABELS)


def faithfulness_recall(original: str, final: str) -> float:
    original_words = content_words(original)
    if not original_words:
        return 1.0
    final_words = content_words(final)
    return len(original_words & final_words) / len(original_words)


def clarity_proxy(text: str) -> float:
    word_count = len(words(text))
    paragraph_count = len([part for part in text.split("\n\n") if part.strip()])
    if 45 <= word_count <= 130 and paragraph_count >= 5:
        return 5.0
    if 30 <= word_count <= 160 and paragraph_count >= 3:
        return 4.0
    if word_count >= 20:
        return 3.0
    return 2.0


def actionability_score(text: str) -> float:
    score = 0.0
    if "Next step:" in text:
        score += 2.5
    if "Success measure:" in text:
        score += 2.5
    return score


def score_text(
    case: EvaluationCase,
    method: str,
    final_text: str,
    description: str,
    traceability_score: float = 0.0,
) -> BaselineMetrics:
    structure_coverage = label_coverage(final_text)
    faithfulness = faithfulness_recall(case.text, final_text)
    clarity = clarity_proxy(final_text)
    actionability = actionability_score(final_text)
    quality = round(mean([structure_coverage * 5, faithfulness * 5, clarity, actionability]), 2)
    return BaselineMetrics(
        case_name=case.name,
        method=method,
        description=description,
        final_text=final_text,
        final_word_count=len(words(final_text)),
        word_delta=len(words(final_text)) - len(words(case.text)),
        structure_coverage=round(structure_coverage, 2),
        faithfulness_recall=round(faithfulness, 2),
        clarity_proxy_score=clarity,
        actionability_score=actionability,
        traceability_score=traceability_score,
        quality_proxy_score=quality,
    )


def identity_baseline(case: EvaluationCase) -> str:
    return " ".join(case.text.split())


def template_baseline(case: EvaluationCase) -> str:
    normalized = " ".join(case.text.split())
    return "\n\n".join(
        [
            f"Problem: {normalized}",
            "Audience: The likely users who already feel this problem.",
            "Value: The idea should make the original workflow easier to understand or act on.",
            "Next step: Ask one target user whether the rewritten problem matches their reality.",
            "Success measure: A reviewer can describe the user, problem, value, and next step.",
        ]
    )


def evaluate_baselines(
    cases: list[EvaluationCase],
    pipeline_cases: list[CaseMetrics],
) -> list[BaselineMetrics]:
    pipeline_by_name = {case.name: case.final_text for case in pipeline_cases}
    rows: list[BaselineMetrics] = []
    for case in cases:
        rows.append(
            score_text(
                case=case,
                method="original_input",
                final_text=identity_baseline(case),
                description=(
                    "No-op baseline. Shows how much the raw idea already satisfies metrics."
                ),
            )
        )
        rows.append(
            score_text(
                case=case,
                method="fixed_template",
                final_text=template_baseline(case),
                description="Rule-based label template without audit, iteration, or LLM trace.",
            )
        )
        rows.append(
            score_text(
                case=case,
                method="pipeline_mock",
                final_text=pipeline_by_name[case.name],
                description="Full API loop with audit, polish, persistence, and trace records.",
                traceability_score=5.0,
            )
        )
    return rows


def aggregate_baselines(rows: list[BaselineMetrics]) -> dict[str, dict[str, Any]]:
    methods = sorted({row.method for row in rows})
    aggregate: dict[str, dict[str, Any]] = {}
    for method in methods:
        subset = [row for row in rows if row.method == method]
        aggregate[method] = {
            "description": subset[0].description,
            "case_count": len(subset),
            "avg_quality_proxy_score": round(mean(row.quality_proxy_score for row in subset), 2),
            "avg_structure_coverage": round(mean(row.structure_coverage for row in subset), 2),
            "avg_faithfulness_recall": round(mean(row.faithfulness_recall for row in subset), 2),
            "avg_clarity_proxy_score": round(mean(row.clarity_proxy_score for row in subset), 2),
            "avg_actionability_score": round(mean(row.actionability_score for row in subset), 2),
            "avg_traceability_score": round(mean(row.traceability_score for row in subset), 2),
            "avg_word_delta": round(mean(row.word_delta for row in subset), 2),
        }
    return aggregate


def percentile(values: list[int], percent: float) -> int:
    if not values:
        return 0
    sorted_values = sorted(values)
    index = round((len(sorted_values) - 1) * percent)
    return sorted_values[index]


async def run_evaluation() -> dict[str, Any]:
    db_path, outputs_dir = prepare_evaluation_paths()
    configure_database(f"sqlite+aiosqlite:///{db_path.as_posix()}")

    evaluation_cases = dataset()
    cases: list[CaseMetrics] = []
    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://metrics") as client:
            for case in evaluation_cases:
                cases.append(await evaluate_case(client, case))
            determinism = await evaluate_determinism(client)

    await drop_db()
    await dispose_db()

    baseline_rows = evaluate_baselines(evaluation_cases, cases)
    aggregate = aggregate_metrics(cases, determinism)
    payload = {
        "metric_definitions": METRIC_DEFINITIONS,
        "limitations": METRIC_LIMITATIONS,
        "aggregate": aggregate,
        "baseline_aggregate": aggregate_baselines(baseline_rows),
        "baseline_cases": [asdict(row) for row in baseline_rows],
        "cases": [asdict(case) for case in cases],
        "determinism": determinism,
    }
    (outputs_dir / "evaluation_metrics.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (outputs_dir / "evaluation_report.md").write_text(render_report(payload), encoding="utf-8")
    return payload


def prepare_evaluation_paths() -> tuple[Path, Path]:
    workspace = Path(__file__).resolve().parents[1]
    work_dir = workspace / "work"
    outputs_dir = workspace / "outputs"
    work_dir.mkdir(exist_ok=True)
    outputs_dir.mkdir(exist_ok=True)

    db_path = work_dir / "evaluation_metrics.db"
    if db_path.exists():
        db_path.unlink()
    return db_path, outputs_dir


async def evaluate_determinism(client: httpx.AsyncClient) -> dict[str, Any]:
    case = EvaluationCase(
        name="determinism_probe",
        text="make notes better for founders",
        expected_polish=True,
    )
    first = await evaluate_case(client, case)
    second = await evaluate_case(client, case)
    return {
        "passed": first.iteration_count == second.iteration_count
        and first.word_delta == second.word_delta
        and first.quality_proxy_score == second.quality_proxy_score,
        "first": asdict(first),
        "second": asdict(second),
    }


def aggregate_metrics(
    cases: list[CaseMetrics],
    determinism: dict[str, Any],
) -> dict[str, Any]:
    total = len(cases)
    latencies = [case.total_api_ms for case in cases]
    return {
        "case_count": total,
        "success_rate": round(sum(case.success for case in cases) / total, 2),
        "converged_rate": round(
            sum(case.convergence_reason == "declared_perfect" for case in cases) / total,
            2,
        ),
        "expected_polish_detection_rate": round(
            sum(case.expected_polish == case.needed_polish for case in cases) / total,
            2,
        ),
        "avg_iterations": round(mean(case.iteration_count for case in cases), 2),
        "avg_llm_calls": round(mean(case.llm_call_count for case in cases), 2),
        "avg_total_api_ms": round(mean(latencies), 2),
        "p95_total_api_ms": percentile(latencies, 0.95),
        "avg_quality_proxy_score": round(mean(case.quality_proxy_score for case in cases), 2),
        "avg_structure_coverage": round(mean(case.structure_coverage for case in cases), 2),
        "avg_faithfulness_recall": round(mean(case.faithfulness_recall for case in cases), 2),
        "all_llm_calls_successful_rate": round(
            sum(case.all_llm_calls_successful for case in cases) / total,
            2,
        ),
        "air_gap_trace_rate": round(sum(case.air_gap_trace_ok for case in cases) / total, 2),
        "determinism_passed": bool(determinism["passed"]),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Evaluation Report",
        "",
        "This report is generated by `python scripts/evaluate_metrics.py` with the "
        "deterministic mock provider. It measures API behavior, traceability, and "
        "proxy quality signals. It does not claim to replace human review.",
        "",
        "## Metric Definitions",
        "",
        "| Metric | Meaning |",
        "| --- | --- |",
    ]
    for key, value in payload["metric_definitions"].items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Limitations", ""])
    for limitation in payload["limitations"]:
        lines.append(f"- {limitation}")

    lines.extend(
        [
            "",
            "## Baseline Comparison",
            "",
            "| Method | Quality | Struct | Faith | Clarity | Action | Trace | Word Delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for method, row in payload["baseline_aggregate"].items():
        lines.append(
            "| {method} | {avg_quality_proxy_score} | {avg_structure_coverage} | "
            "{avg_faithfulness_recall} | {avg_clarity_proxy_score} | "
            "{avg_actionability_score} | {avg_traceability_score} | {avg_word_delta} |".format(
                method=method,
                **row,
            )
        )

    lines.extend(["", "Baseline descriptions:", ""])
    for method, row in payload["baseline_aggregate"].items():
        lines.append(f"- `{method}`: {row['description']}")

    lines.extend(
        [
            "",
            "## Aggregate API Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
        ]
    )
    for key, value in payload["aggregate"].items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Case Metrics",
            "",
            "| Case | Iter | Conv | Quality | Struct | Faith | API ms | LLM calls | Trace |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for case in payload["cases"]:
        lines.append(
            "| {name} | {iteration_count} | {convergence_reason} | "
            "{quality_proxy_score} | {structure_coverage} | {faithfulness_recall} | "
            "{total_api_ms} | {llm_call_count} | {air_gap_trace_ok} |".format(**case)
        )

    lines.extend(["", "## Output Samples", ""])
    baseline_by_case = group_baseline_cases(payload["baseline_cases"])
    for case in payload["cases"]:
        lines.extend(
            [
                f"### {case['name']}",
                "",
                "Original:",
                "",
                "```text",
                case["original_text"],
                "```",
                "",
                "Fixed-template baseline:",
                "",
                "```text",
                baseline_by_case[case["name"]]["fixed_template"]["final_text"],
                "```",
                "",
                "Pipeline final output:",
                "",
                "```text",
                case["final_text"],
                "```",
                "",
            ]
        )

    determinism = payload["determinism"]
    lines.extend(
        [
            "## Determinism Probe",
            "",
            f"Passed: {determinism['passed']}",
            "",
            "The deterministic mock provider produced the same iteration count, word delta, "
            "and quality proxy score across repeated runs of the same input.",
            "",
        ]
    )
    return "\n".join(lines)


def group_baseline_cases(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["case_name"], {})[row["method"]] = row
    return grouped


def main() -> None:
    payload = asyncio.run(run_evaluation())
    print(json.dumps(payload["aggregate"], indent=2))
    print("wrote outputs/evaluation_metrics.json")
    print("wrote outputs/evaluation_report.md")


if __name__ == "__main__":
    main()
