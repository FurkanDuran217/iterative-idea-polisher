from __future__ import annotations

import hashlib
import re


def normalize_input_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_model_text(text: str) -> str:
    text = _strip_model_meta_explanation(text)
    text = _normalize_markdown_labels(text)
    lines = [line.strip() for line in text.strip().splitlines()]
    compact_lines: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = line == ""
        if is_blank and previous_blank:
            continue
        compact_lines.append(line)
        previous_blank = is_blank
    return "\n".join(compact_lines).strip()


def _strip_model_meta_explanation(text: str) -> str:
    meta_patterns = (
        r"\n\s*I made the following changes\s*:",
        r"\n\s*Changes made\s*:",
        r"\n\s*Here(?:'s| is) what I changed\s*:",
    )
    earliest_marker: int | None = None
    for pattern in meta_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match and (earliest_marker is None or match.start() < earliest_marker):
            earliest_marker = match.start()
    if earliest_marker is not None:
        return text[:earliest_marker]
    return text


def _normalize_markdown_labels(text: str) -> str:
    labels = ("Problem", "Audience", "Value", "Next step", "Success measure")
    for label in labels:
        text = re.sub(rf"\*\*{re.escape(label)}\*\*\s*:", f"{label}:", text)
    return text


def stable_hash(*parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()
