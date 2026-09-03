# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.
Replace this paragraph with a one-line description of what the repo is and does.

## Repository Overview

Brief description of the project, its purpose, and primary language(s).

## Language Rules

Rules the linter flags but cannot auto-fix. These must be correct at write
time. Remove sections that do not apply to this repo's language stack.

See [Code Formatting Rules](https://github.com/Positronikal/PositronikalCodingStandards/blob/main/standards/Code%20Formatting%20Rules.md)
for the full Tier 1/Tier 2 framework.

### Python

- **S603/S607** — `subprocess` calls: annotate `# noqa: S603` and `# noqa: S607`
  only when the input is trusted and the call is intentional. Never suppress
  without a documented reason in an adjacent comment.
- **S110** — Empty `except` blocks: always add meaningful error handling.
  `# noqa: S110` requires a comment explaining why silence is correct.
- **C901** — Cyclomatic complexity: restructure before suppressing.
  `# noqa: C901` requires a comment explaining why the complexity is unavoidable.
- **Intentional `# noqa`** — Every suppression annotation must have an adjacent
  comment stating why the rule does not apply in that instance.

### Go

- **Error returns** — Every error return must be explicitly handled or assigned
  to `_` with an adjacent comment explaining why it is safe to discard.
- **`defer` in loops** — Avoid; if unavoidable, document the resource lifecycle.
- **Context** — Use `context.Background()` at top-level entry points;
  `context.TODO()` only as a placeholder during active development.

### PowerShell

- **Approved verbs** — Use PSScriptAnalyzer-approved verbs only. Run
  `Get-Verb` for the full list. Common approved: `Get-`, `Set-`, `New-`,
  `Remove-`, `Add-`, `Clear-`, `Start-`, `Stop-`, `Invoke-`, `Out-`,
  `Write-`, `Read-`, `Format-`, `Import-`, `Export-`, `Select-`, `Test-`.
- **No empty `catch` blocks** — `catch { }` and `catch { $null = $_ }` are
  violations. Always add meaningful error handling.
- **No aliases** — Use full cmdlet names in all scripts (`Get-ChildItem`,
  not `ls` or `dir`).
- **Advanced functions** — Include `[CmdletBinding()]` on all advanced functions.

### bash/shell

- **`# shellcheck disable=`** — Every suppression must have an adjacent comment
  stating why the flagged pattern is safe in this context. Never suppress to
  silence a genuine warning.

## Development Notes

Add repo-specific context here: key invariants, known constraints, working
arrangements (e.g. two-location install), or anything a cold-start session
needs to know before editing files.
