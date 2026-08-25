MAIN := parser.py

MAP ?= maps/hard/02_capacity_hell.txt
MODE ?= pygame

RUN_MAP := $(if $(filter /%,$(MAP)),$(MAP),$(if $(filter maps/%,$(MAP)),$(MAP),maps/$(MAP)))

.PHONY: install sync run debug clean lint lint-strict add-dev

install:
	uv sync

sync:
	uv sync

run:
	uv run python $(MAIN) "$(RUN_MAP)" $(MODE)

debug:
	uv run python -m pdb $(MAIN) "$(RUN_MAP)" $(MODE)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".venv" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 models.py parser.py visualizer.py
	uv run mypy models.py parser.py visualizer.py \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	uv run flake8 models.py parser.py visualizer.py
	uv run mypy models.py parser.py visualizer.py --strict