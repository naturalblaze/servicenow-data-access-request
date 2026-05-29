.PHONY: help install install-dev test test-cov test-cov-html lint format clean run

help:
	@echo "ServiceNow Data Access Request - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install         Install project dependencies"
	@echo "  make install-dev     Install development dependencies"
	@echo "  make test            Run unit tests"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make test-cov-html   Generate HTML coverage report"
	@echo "  make lint            Run code quality checks (flake8, mypy)"
	@echo "  make format          Format code with black"
	@echo "  make clean           Clean up temporary files and caches"
	@echo "  make run             Run the application"

install:
	.venv/bin/pip install -r requirements.txt

install-dev:
	.venv/bin/pip install -r requirements-dev.txt

test:
	.venv/bin/pytest tests/ -v

test-cov:
	.venv/bin/pytest tests/ -v --cov=. --cov-report=term-missing

test-cov-html:
	.venv/bin/pytest tests/ -v --cov=. --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running flake8..."
	.venv/bin/flake8 api gui scheduler --max-line-length=120
	@echo "Running mypy..."
	.venv/bin/mypy api gui scheduler --ignore-missing-imports || true

format:
	.venv/bin/black api gui scheduler main.py

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	find . -type d -name '.coverage' -delete
	rm -rf htmlcov/ .coverage

pip-export:
	@uv export --no-dev --no-emit-project --no-editable > requirements.txt
	@uv export --dev --no-emit-project --no-editable > requirements-dev.txt

run:
	.venv/bin/python main.py
