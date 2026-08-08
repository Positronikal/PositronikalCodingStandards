#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Single source of truth for CI/code-quality checks.
# Invoked locally by hooks/pre-push (blocking) and by .github/workflows/ci.yml
# (confirmation only). Both run this exact script so local and CI cannot drift.
set -e

uv sync --extra dev

echo "Running tests..."
uv run python -m pytest \
    positronikal_standards_check/tests/test_standards.py

echo "Linting with Ruff..."
uv run python -m ruff check positronikal_standards_check/
uv run python -m ruff format positronikal_standards_check/ --check

echo "Security vulnerability scan (safety)..."
uv run python -m safety check --json \
    || echo "Safety check completed with warnings"

echo "ci-check passed."
