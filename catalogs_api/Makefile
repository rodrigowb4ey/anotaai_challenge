.PHONY: all format lint

all: format lint

format:
	ruff format .

lint:
	ruff check .
	mypy --show-error-context --pretty .