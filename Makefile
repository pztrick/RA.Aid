# Use bash as the shell for all commands
SHELL := /bin/bash

# Virtual environment directory
VENV := .venv

# Define executables from the virtual environment
VENV_PYTHON := $(VENV)/bin/python
VENV_RUFF := $(VENV)/bin/ruff
VENV_PRE_COMMIT := $(VENV)/bin/pre-commit

# Phony targets - list all targets that are not files
.PHONY: all-costs check clean extract-plan extract-last-plan extract-last-research-notes fix fix-basic help last-cost migrate migrate-create migrate-status setup-dev setup-dev-uv setup-hooks test

# ====================================================================================
# HELP
# ====================================================================================
help:
	@echo "Available targets:"
	@echo ""
	@echo "  Setup (run first!):"
	@echo "    setup-dev                 - Create venv using standard 'pip' and install dependencies"
	@echo "    setup-dev-uv              - Create venv using 'uv' and install dependencies"
	@echo "    setup-hooks               - Install git pre-commit hooks (run after setup-dev)"
	@echo ""
	@echo "  Quality & Testing:"
	@echo "    test                      - Run tests with coverage reporting"
	@echo "    check                     - Run code quality checks with ruff"
	@echo "    fix                       - Fix code style issues automatically"
	@echo "    fix-basic                 - Fix basic code style issues"
	@echo ""
	@echo "  Database:"
	@echo "    migrate-create name=...   - Create a new database migration (e.g., make migrate-create name=add_new_field)"
	@echo "    migrate                   - Run all pending database migrations"
	@echo "    migrate-status            - Show the current status of database migrations"
	@echo ""
	@echo "  Application Scripts:"
	@echo "    last-cost                 - Display cost and token usage for the latest session"
	@echo "    all-costs                 - Display cost and token usage for all sessions"
	@echo "    extract-plan session_id=... - Extract the plan for a given session_id (e.g., make extract-plan session_id=1)"
	@echo "    extract-last-plan         - Extract the plan for the most recent session"
	@echo "    extract-last-research-notes - Extract research notes for the most recent session"
	@echo ""
	@echo "  Housekeeping:"
	@echo "    clean                     - Remove the virtual environment and build artifacts"


# ====================================================================================
# SETUP
# ====================================================================================

# Install development dependencies using standard pip.
setup-dev:
	@echo "--> Creating virtual environment using python venv..."
	python -m venv $(VENV)
	@echo "--> Installing dependencies using pip..."
	$(VENV_PYTHON) -m pip install -e ".[dev]"
	@echo "Setup complete. Virtual environment is ready."

# Install development dependencies using uv.
setup-dev-uv:
	@if ! command -v uv &> /dev/null; then \
		echo "Error: 'uv' is not installed. Please install it first."; \
		echo "See: https://github.com/astral-sh/uv"; \
		exit 1; \
	fi
	@echo "--> Creating virtual environment using uv..."
	uv venv
	@echo "--> Installing dependencies using uv..."
	uv pip install -e ".[dev]"
	@echo "Setup complete. Virtual environment is ready."

setup-hooks: setup-dev
	$(VENV_PRE_COMMIT) install


# ====================================================================================
# QUALITY & TESTING
# ====================================================================================

test:
	# for future consideration append  --cov-fail-under=80 to fail test coverage if below 80%
	@echo "--> Running tests..."
	$(VENV_PYTHON) -m pytest --cov=ra_aid --cov-report=term-missing --cov-report=html

check:
	@echo "--> Checking code quality with ruff..."
	$(VENV_RUFF) check

fix:
	@echo "--> Formatting and fixing code with ruff..."
	$(VENV_RUFF) check . --select I --fix # First sort imports
	$(VENV_RUFF) format .
	$(VENV_RUFF) check --fix

fix-basic:
	@echo "--> Fixing basic issues with ruff..."
	$(VENV_RUFF) check --fix


# ====================================================================================
# DATABASE
# ====================================================================================

migrate-create:
	@echo "--> Creating migration: $(name)"
	$(VENV_PYTHON) -m ra_aid create-migration $(name)

migrate:
	@echo "--> Running database migrations..."
	$(VENV_PYTHON) -m ra_aid migrate

migrate-status:
	@echo "--> Checking migration status..."
	$(VENV_PYTHON) -m ra_aid migration-status


# ====================================================================================
# APPLICATION SCRIPTS
# ====================================================================================

extract-last-plan:
	@$(VENV_PYTHON) -m ra_aid extract-last-plan

extract-last-research-notes:
	@$(VENV_PYTHON) -m ra_aid extract-last-research-notes

last-cost:
	$(VENV_PYTHON) -m ra_aid last-cost

all-costs:
	$(VENV_PYTHON) -m ra_aid all-costs

extract-plan:
	@if [ -z "$(session_id)" ]; then \
		$(VENV_PYTHON) -m ra_aid extract-plan; \
	else \
		$(VENV_PYTHON) -m ra_aid extract-plan $(session_id); \
	fi




# ====================================================================================
# HOUSEKEEPING
# ====================================================================================

clean:
	rm -rf $(VENV) .pytest_cache htmlcov .coverage .ruff_cache
	find . -type d -name "__pycache__" -exec rm -r {} +
	@echo "Cleaned up virtual environment and build artifacts."
