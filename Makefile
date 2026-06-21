PY := uv run
MAIN := parser.py

.PHONY: install sync run debug clean lint lint-strict add-dev

install:
	uv sync

run:
	$(PY) python $(MAIN)

debug:
	$(PY) python -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(PY) flake8 .
	$(PY) mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PY) flake8 .
	$(PY) mypy . --strict