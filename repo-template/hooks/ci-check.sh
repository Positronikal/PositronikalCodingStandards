#!/usr/bin/env bash
# Single source of truth for CI/code-quality checks.
# Invoked locally by hooks/pre-push (blocking) and by .github/workflows/ci.yml
# (confirmation only) — both must run this exact script so local and CI cannot
# drift. Replace the body below with the repository's actual checks (lint,
# type-check, tests, SAST, dependency/license scan) for its language.
set -e

echo "ci-check: no checks configured yet."
echo "  See standards/Git Hooks Standards.md and davinci-mcp-professional's"
echo "  hooks/ci-check.sh for a worked Python example."

echo "ci-check passed."
