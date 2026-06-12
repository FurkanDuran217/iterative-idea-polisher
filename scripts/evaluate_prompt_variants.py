from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean


@dataclass(frozen=True)
class PromptVariant:
    prompt_type: str
    name: str
    summary: str
    representative_output: str
    parse_reliability: int
    convergence_control: int
    faithfulness_control: int
    reviewer_clarity: int
    selected: bool
    decision: str

    @property
    def score(self) -> float:
        return round(
            mean(
                [
                    self.parse_reliability,
                    self.convergence_control,
                    self.faithfulness_control,
                    self.reviewer_clarity,
                ]
            ),
            2,
        )


def variants() -> list[PromptVariant]:
    return [
        PromptVariant(
            prompt_type="audit",
            name="audit.loose_v0",
            summary="Asks for improvements in natural language without a schema.",
            representative_output=(
                "The idea is too vague. You should add a target user, the main problem, "
                "and a way to measure success."
            ),
            parse_reliability=1,
            convergence_control=2,
            faithfulness_control=3,
            reviewer_clarity=3,
            selected=False,
            decision=(
                "Rejected because free-form audit text forces brittle parsing and makes "
                "retry behavior harder to prove."
            ),
        ),
        PromptVariant(
            prompt_type="audit",
            name="audit.verdict_json_v2",
            summary="Requires JSON with perfection verdict, score, rationale, and suggestions.",
            representative_output=(
                '{"is_perfect":false,"quality_score":72,'
                '"rationale":"The idea needs a clearer user and metric.",'
                '"suggestions":["Add a clear target audience.",'
                '"Add a measurable success criterion."]}'
            ),
            parse_reliability=5,
            convergence_control=5,
            faithfulness_control=4,
            reviewer_clarity=5,
            selected=True,
            decision=(
                "Selected because the model explicitly declares whether the text is perfect, "
                "while still giving concrete edits when it is not."
            ),
        ),
        PromptVariant(
            prompt_type="audit",
            name="audit.rubric_json_v2",
            summary="Returns JSON suggestions plus per-rubric scores.",
            representative_output=(
                '{"scores":{"clarity":3,"specificity":2,"actionability":2},'
                '"suggestions":["Clarify the audience.","Make the next step testable."]}'
            ),
            parse_reliability=4,
            convergence_control=3,
            faithfulness_control=4,
            reviewer_clarity=5,
            selected=False,
            decision=(
                "Useful for a later product version, but it adds scope and can encourage "
                "new style critiques after the core structure is already fixed."
            ),
        ),
        PromptVariant(
            prompt_type="polish",
            name="polish.verbose_v0",
            summary="Allows explanation before and after the rewritten text.",
            representative_output=(
                "Here is a clearer version:\n\nProblem: ...\n\nThis works because it is "
                "more specific."
            ),
            parse_reliability=2,
            convergence_control=2,
            faithfulness_control=3,
            reviewer_clarity=3,
            selected=False,
            decision=(
                "Rejected because extra explanation contaminates the stored text version and "
                "makes downstream audits judge meta-commentary."
            ),
        ),
        PromptVariant(
            prompt_type="polish",
            name="polish.idea_brief_v2",
            summary="Returns only a structured idea brief after applying the audit verdict.",
            representative_output=(
                "Problem: Founders collect notes but struggle to turn them into a clear next "
                "action.\n\nAudience: Early-stage founders..."
            ),
            parse_reliability=5,
            convergence_control=5,
            faithfulness_control=5,
            reviewer_clarity=5,
            selected=True,
            decision=(
                "Selected because the next air-gapped audit should judge only the candidate "
                "text, not the model's explanation of the edit."
            ),
        ),
        PromptVariant(
            prompt_type="polish",
            name="polish.creative_v2",
            summary="Encourages stronger product language and novelty.",
            representative_output=(
                "Launch a founder intelligence cockpit that transforms chaotic notes into "
                "board-ready insight loops."
            ),
            parse_reliability=5,
            convergence_control=3,
            faithfulness_control=2,
            reviewer_clarity=4,
            selected=False,
            decision=(
                "Rejected for this task because creativity can drift away from the user's "
                "original idea and inflate perceived quality."
            ),
        ),
    ]


def run_evaluation() -> dict[str, object]:
    rows = variants()
    selected = [row for row in rows if row.selected]
    payload: dict[str, object] = {
        "method": "offline prompt-design evaluation",
        "score_scale": "1=weak, 5=strong",
        "selected_pair": [row.name for row in selected],
        "selection_rationale": (
            "The selected pair optimizes for explicit perfection decisions, parse reliability, "
            "traceability, and low contamination of stored text versions. Richer rubric prompts "
            "are documented as future work because they create a larger evaluation surface."
        ),
        "variants": [
            {
                **asdict(row),
                "score": row.score,
            }
            for row in rows
        ],
        "aggregate_by_type": aggregate_by_type(rows),
    }
    return payload


def aggregate_by_type(rows: list[PromptVariant]) -> dict[str, dict[str, float]]:
    types = sorted({row.prompt_type for row in rows})
    aggregate: dict[str, dict[str, float]] = {}
    for prompt_type in types:
        subset = [row for row in rows if row.prompt_type == prompt_type]
        aggregate[prompt_type] = {
            "avg_score": round(mean(row.score for row in subset), 2),
            "selected_score": round(mean(row.score for row in subset if row.selected), 2),
        }
    return aggregate


def render_report(payload: dict[str, object]) -> str:
    variants_payload = payload["variants"]
    if not isinstance(variants_payload, list):
        raise TypeError("variants payload must be a list")

    lines = [
        "# Prompt Variant Evaluation",
        "",
        "This is an offline prompt-design evaluation. It explains why the current prompts "
        "were selected before running the app with a live provider.",
        "",
        f"Selected pair: `{', '.join(str(name) for name in payload['selected_pair'])}`",
        "",
        str(payload["selection_rationale"]),
        "",
        "## Comparison",
        "",
        "| Type | Variant | Selected | Score | Parse | Convergence | Faithfulness | Clarity |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in variants_payload:
        lines.append(
            "| {prompt_type} | {name} | {selected} | {score} | {parse_reliability} | "
            "{convergence_control} | {faithfulness_control} | {reviewer_clarity} |".format(
                **row
            )
        )

    lines.extend(["", "## Decisions", ""])
    for row in variants_payload:
        lines.extend(
            [
                f"### {row['name']}",
                "",
                row["summary"],
                "",
                "Representative output:",
                "",
                "```text",
                row["representative_output"],
                "```",
                "",
                row["decision"],
                "",
            ]
        )
    return "\n".join(lines)


def write_outputs(payload: dict[str, object]) -> None:
    outputs_dir = Path(__file__).resolve().parents[1] / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    (outputs_dir / "prompt_variant_evaluation.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (outputs_dir / "prompt_variant_report.md").write_text(
        render_report(payload),
        encoding="utf-8",
    )


def main() -> None:
    payload = run_evaluation()
    write_outputs(payload)
    print(json.dumps(payload["aggregate_by_type"], indent=2))
    print("wrote outputs/prompt_variant_evaluation.json")
    print("wrote outputs/prompt_variant_report.md")


if __name__ == "__main__":
    main()
