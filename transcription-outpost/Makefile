.PHONY: help install test lint format security clean run-tests pre-commit

help: ## 🎖️ Show this help message
	@echo "🎖️ Transcription Outpost Development Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 🎖️ Install dependencies
	poetry install
	poetry run pre-commit install

test: ## 🎖️ Run full test battalion
	poetry run python run_tests.py

test-unit: ## 🎖️ Run unit tests only
	poetry run pytest tests/services/ -v

test-api: ## 🎖️ Run API integration tests
	poetry run pytest tests/test_api_integration.py -v

test-fast: ## 🎖️ Run tests with minimal output
	poetry run pytest tests/ -q

test-coverage: ## 🎖️ Run tests with coverage report
	poetry run pytest --cov=app --cov-report=html --cov-report=term tests/

lint: ## 🎖️ Run linting checks
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 .

format: ## 🎖️ Auto-format code
	poetry run black .
	poetry run isort .

security: ## 🎖️ Run security scans
	poetry run safety check
	poetry run bandit -r app/

clean: ## 🎖️ Clean up cache and temp files
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov/

run-tests: test ## 🎖️ Alias for test command

pre-commit: ## 🎖️ Run pre-commit hooks manually
	poetry run pre-commit run --all-files

watch-tests: ## 🎖️ Watch for changes and run tests
	poetry run ptw tests/ -- -v

dev-server: ## 🎖️ Start development server
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

prod-server: ## 🎖️ Start production server
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 