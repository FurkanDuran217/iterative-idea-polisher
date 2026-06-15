from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import mean

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


@dataclass(frozen=True)
class TextReviewScore:
    word_count: int
    structure_coverage: float
    faithfulness_recall: float
    clarity_proxy_score: float
    actionability_score: float
    quality_proxy_score: float


def score_text_against_original(original: str, text: str) -> TextReviewScore:
    structure_coverage = _label_coverage(text)
    faithfulness = _faithfulness_recall(original, text)
    clarity = _clarity_proxy(text)
    actionability = _actionability_score(text)
    quality = round(mean([structure_coverage * 5, faithfulness * 5, clarity, actionability]), 2)
    return TextReviewScore(
        word_count=len(_words(text)),
        structure_coverage=round(structure_coverage, 2),
        faithfulness_recall=round(faithfulness, 2),
        clarity_proxy_score=clarity,
        actionability_score=actionability,
        quality_proxy_score=quality,
    )


def review_decision(
    *,
    original_score: TextReviewScore,
    current_score: TextReviewScore,
    status: str,
    air_gap_trace_ok: bool,
) -> tuple[bool, str]:
    quality_delta = current_score.quality_proxy_score - original_score.quality_proxy_score
    likely_better = (
        quality_delta > 0
        and current_score.faithfulness_recall >= 0.5
        and current_score.actionability_score >= original_score.actionability_score
    )
    if status == "completed" and likely_better and air_gap_trace_ok:
        return (
            True,
            "The final text scores higher on the deterministic review rubric, preserves the "
            "original intent, and has a complete air-gap trace.",
        )
    if likely_better:
        return (
            True,
            "The current text scores higher on the deterministic review rubric, but the result "
            "still needs human review before treating it as objectively better.",
        )
    return (
        False,
        "The deterministic rubric does not yet show a clear improvement over the original.",
    )


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def _content_words(text: str) -> set[str]:
    return {word for word in _words(text) if word not in STOP_WORDS and len(word) > 2}


def _label_coverage(text: str) -> float:
    return sum(1 for label in REQUIRED_LABELS if label in text) / len(REQUIRED_LABELS)


def _faithfulness_recall(original: str, text: str) -> float:
    original_words = _content_words(original)
    if not original_words:
        return 1.0
    text_words = _content_words(text)
    return len(original_words & text_words) / len(original_words)


def _clarity_proxy(text: str) -> float:
    word_count = len(_words(text))
    paragraph_count = len([part for part in text.split("\n\n") if part.strip()])
    if 45 <= word_count <= 130 and paragraph_count >= 5:
        return 5.0
    if 30 <= word_count <= 160 and paragraph_count >= 3:
        return 4.0
    if word_count >= 20:
        return 3.0
    return 2.0


def _actionability_score(text: str) -> float:
    score = 0.0
    if "Next step:" in text:
        score += 2.5
    if "Success measure:" in text:
        score += 2.5
    return score
