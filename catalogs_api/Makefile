.PHONY: all format lint

all: format lint

format:
	ruff format .

lint:
	ruff check . --fix
	mypy --show-error-context --pretty .