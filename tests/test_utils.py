from __future__ import annotations

from videoedgeai_task.utils import normalize_model_text


def test_normalize_model_text_strips_meta_explanation() -> None:
    text = "Problem: clear\n\nI made the following changes:\n- tightened it"

    assert normalize_model_text(text) == "Problem: clear"


def test_normalize_model_text_flattens_markdown_labels() -> None:
    text = "**Problem**: messy notes\n\n**Success measure**: reviewer understands it"

    assert normalize_model_text(text) == (
        "Problem: messy notes\n\nSuccess measure: reviewer understands it"
    )
