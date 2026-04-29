# ============================================================
# NarrowGate (窄门) — Makefile
# Common development tasks
# ============================================================

.PHONY: help install dev test test-cov lint format run clean

PYTHON      := python3
PIP         := pip3
SRC_DIR     := src
TEST_DIR    := tests
VENV_DIR    := venv

# Default target
help: ## Show this help message
	@echo "窄门 NarrowGate — Development Commands"
	@echo "======================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ============================================================
# Setup
# ============================================================

install: ## Install production dependencies
	$(PIP) install -r requirements.txt

dev: ## Install development dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov httpx ruff mypy

venv: ## Create and activate a virtual environment
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Run: source $(VENV_DIR)/bin/activate"

# ============================================================
# Testing
# ============================================================

test: ## Run all tests
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest $(TEST_DIR)/ -v

test-quick: ## Run tests excluding slow ones
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest $(TEST_DIR)/ -v -m "not slow"

test-cov: ## Run tests with coverage report
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		-v

test-core: ## Run only core module tests
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest $(TEST_DIR)/test_core.py -v

test-api: ## Run only API tests
	PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest $(TEST_DIR)/test_api.py -v

# ============================================================
# Code Quality
# ============================================================

lint: ## Run ruff linter
	ruff check $(SRC_DIR)/ $(TEST_DIR)/

format: ## Run ruff formatter
	ruff format $(SRC_DIR)/ $(TEST_DIR)/

format-check: ## Check formatting without modifying
	ruff format --check $(SRC_DIR)/ $(TEST_DIR)/

typecheck: ## Run mypy type checker
	mypy $(SRC_DIR)/ --ignore-missing-imports

check: lint format-check typecheck ## Run all code quality checks

# ============================================================
# Run
# ============================================================

run: ## Start the development server
	cd $(SRC_DIR)/api && $(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8090

run-prod: ## Start the production server
	cd $(SRC_DIR)/api && $(PYTHON) -m uvicorn main:app --host 127.0.0.1 --port 8090 --workers 2

# ============================================================
# Cleanup
# ============================================================

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .mypy_cache .ruff_cache
	rm -f coverage.xml
	@echo "Cleaned build artifacts"

clean-data: ## Remove local database (WARNING: destroys all data)
	rm -f data/narrowgate.db
	@echo "Database removed"

# ============================================================
# Documentation
# ============================================================

docs-serve: ## Open documentation
	@echo "Documentation files:"
	@ls -la docs/
	@echo ""
	@echo "Open docs/THEORY.md for the complete methodology"
