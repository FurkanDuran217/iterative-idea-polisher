# Versioning

This project uses semantic versioning.

- `v0.1.0`: baseline implementation that satisfies the exercise and passes tests/metrics.
- `v0.2.0`: excellence pass with CI, reviewer-facing metrics, and stronger documentation.
- `v0.3.0`: rename pass for the final `VideoEdgeAI-Task` project identity.
- `v0.4.0`: traceability and failure-hardening pass for LLM calls.
- `v0.5.0`: baseline evaluation and prompt-variant experiment pass.
- `v0.6.0`: reviewer console UI pass.
- `v0.6.1`: Windows reviewer-console launch helper pass.
- `v0.6.2`: reviewer console usability pass.
- `v0.7.0`: smart audit verdict and UI clarity pass.
- `v0.8.0`: request-level provider override and reviewer-console provider selection pass.
- `v0.9.0`: Ollama local LLM and OpenAI-compatible provider pass.

Suggested release workflow:

```bash
pytest
ruff check .
mypy src
python scripts/evaluate_metrics.py
python scripts/evaluate_prompt_variants.py
git tag -a vX.Y.Z -m "vX.Y.Z description"
```

The local baseline tag is intentionally kept so reviewers can compare the first complete solution
with later polish.
