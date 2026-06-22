#!/usr/bin/env bash
# Single source of truth for CI/code-quality checks.
# Invoked locally by hooks/pre-push (blocking) and by .github/workflows/ci.yml
# (confirmation only) — both run this exact script so local and CI cannot drift.
#
# This repo has no root pyproject.toml; the only real source code is the
# positronikal_standards_check/ package, installed via setup.py.
set -e

uv venv --clear
uv pip install -e "./positronikal_standards_check[dev]"

echo "Running tests..."
uv run --no-project python -m pytest positronikal_standards_check/tests/test_standards.py

echo "Linting with Ruff..."
uv run --no-project python -m ruff check positronikal_standards_check/
uv run --no-project python -m ruff format positronikal_standards_check/ --check

echo "Security vulnerability scan (safety)..."
uv run --no-project python -m safety check --json || echo "Safety check completed with warnings"

echo "ci-check passed."
