from __future__ import annotations

import hashlib
import re


def normalize_input_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_model_text(text: str) -> str:
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


def stable_hash(*parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()

