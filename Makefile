.PHONY: install dev test lint typecheck run demo metrics quality clean

install:
	python -m pip install -e ".[dev]"

dev:
	uvicorn idea_polisher.main:app --reload

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy src

run:
	uvicorn idea_polisher.main:app --host 0.0.0.0 --port 8000

demo:
	python scripts/demo.py

metrics:
	python scripts/evaluate_metrics.py

quality:
	python scripts/quality_gate.py

clean:
	python -c "from pathlib import Path; [p.unlink() for p in Path('.').glob('*.db')]"
