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
- `v0.9.1`: Ollama prompt convergence fix after a real local model run.
- `v0.10.0`: Gemini and Claude provider pass with server-default Gemini support and UI help.
- `v0.10.1`: provider help usability pass with actionable setup guidance in the console.
- `v0.11.0`: Gemini default UX and prompt pass with click-to-open provider setup help.
- `v0.12.0`: reviewer report and similar-system analysis pass.
- `v0.13.0`: air-gap prompt engineering analysis with real endpoint outputs and case matrix.
- `v0.14.0`: domain coverage expansion (10 domains) and 16-case system performance analysis.

Suggested release workflow:

```bash
pytest
ruff check .
mypy src
python scripts/evaluate_metrics.py
python scripts/evaluate_prompt_variants.py
python scripts/evaluate_air_gap_cases.py --write-docs
git tag -a vX.Y.Z -m "vX.Y.Z description"
```

The local baseline tag is intentionally kept so reviewers can compare the first complete solution
with later polish.
