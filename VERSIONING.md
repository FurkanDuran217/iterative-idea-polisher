# Versioning

This project uses semantic versioning.

- `v0.1.0`: baseline implementation that satisfies the exercise and passes tests/metrics.
- `v0.2.0`: excellence pass with CI, reviewer-facing metrics, and stronger documentation.
- `v0.3.0`: rename pass for the final `VideoEdgeAI-Task` project identity.

Suggested release workflow:

```bash
pytest
ruff check .
mypy src
python scripts/evaluate_metrics.py
git tag -a vX.Y.Z -m "vX.Y.Z description"
```

The local baseline tag is intentionally kept so reviewers can compare the first complete solution
with later polish.
