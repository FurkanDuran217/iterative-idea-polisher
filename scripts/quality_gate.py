from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    name: str
    command: list[str]
    return_code: int
    elapsed_ms: int


def run_check(name: str, command: list[str]) -> CheckResult:
    start = time.perf_counter()
    completed = subprocess.run(command, check=False)
    elapsed_ms = round((time.perf_counter() - start) * 1000)
    return CheckResult(
        name=name,
        command=command,
        return_code=completed.returncode,
        elapsed_ms=elapsed_ms,
    )


def main() -> int:
    checks = [
        ("tests", [sys.executable, "-m", "pytest"]),
        ("lint", ["ruff", "check", "."]),
        ("typecheck", ["mypy", "src"]),
        ("metrics", [sys.executable, "scripts/evaluate_metrics.py"]),
    ]
    results = [run_check(name, command) for name, command in checks]
    payload = {
        "passed": all(result.return_code == 0 for result in results),
        "checks": [asdict(result) for result in results],
    }
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    (outputs_dir / "quality_gate.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

