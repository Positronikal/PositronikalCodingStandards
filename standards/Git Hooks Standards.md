# Git Hooks Standards

## Objective

Establish standardized Git hooks to automatically enforce coding standards and quality gates at the developer level. Hooks provide immediate feedback and catch issues before they reach a remote repository.

See [COMMON.md](./COMMON.md) for common exceptions. These standards do not apply to contributing forks.

## Hook Architecture

Three gates apply to all Positronikal repositories:

| Hook | Trigger | Purpose | Blocking |
|------|---------|---------|---------|
| `pre-commit` | Every commit | Fast, language-native formatting and static analysis | Yes |
| `commit-msg` | Every commit | Conventional commit message format | Yes |
| `pre-push` | Before push to remote | Local CI/CD gate (`hooks/ci-check.sh`) + semantic security review via Claude Code | Yes (CI/CD gate); No (security review) |

The pre-commit and commit-msg hooks block the commit on failure. The `pre-push` security review is informational — it displays findings but does not prevent the push.

**Local CI/CD is the gate; GitHub Actions is confirmation only.** `hooks/ci-check.sh` is the single source of truth for code-quality checks (lint, type-check, tests, SAST, dependency/license scan). It is invoked twice: by the blocking local `pre-push` hook, and by `.github/workflows/ci.yml` — both run the exact same script, so a local pass reliably predicts the CI verdict for the same commit. This is a deliberate alternative to GitHub-side gating (`required_pull_request_reviews`, `required_status_checks`): those block direct pushes outright or add a checkbox that does nothing once local CI/CD already gates the push, respectively. See [GitHub Configuration Standards](./GitHub%20Configuration%20Standards.md) for the branch-protection model this pairs with. GitHub-native security analysis (CodeQL, Dependabot) is independent of this gate and remains GitHub's own responsibility.

## Pre-Commit Hook

The pre-commit hook runs fast, language-native checks. It should complete in seconds. Adapt the template below for the repository's primary language.

### Go

```bash
#!/usr/bin/env bash
set -e

unformatted=$(gofmt -l .)
if [ -n "$unformatted" ]; then
    echo "Unformatted Go files:"
    echo "$unformatted"
    echo "Run: gofmt -w ."
    exit 1
fi

go vet ./...
echo "Pre-commit checks passed."
```

### Python

```bash
#!/usr/bin/env bash
set -e

ruff check .
ruff format --check .
echo "Pre-commit checks passed."
```

### C

```bash
#!/usr/bin/env bash
set -e

cppcheck --error-exitcode=1 --enable=warning,style src/
echo "Pre-commit checks passed."
```

### bash/shell

```bash
#!/usr/bin/env bash
set -e

changed=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.sh$' || true)
if [ -n "$changed" ]; then
    echo "$changed" | xargs shellcheck
fi
echo "Pre-commit checks passed."
```

### PowerShell

```bash
#!/usr/bin/env bash
set -e

changed=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.ps1$' || true)
if [ -n "$changed" ]; then
    echo "$changed" | while read -r f; do
        pwsh -Command "Invoke-ScriptAnalyzer -Path '$f' -Severity Error"
    done
fi
echo "Pre-commit checks passed."
```

### Secret Scanning

Append to any pre-commit hook, after language checks:

```bash
# Secret scanning (gitleaks)
if command -v gitleaks >/dev/null 2>&1; then
    if ! gitleaks protect --staged --no-banner; then
        echo "Secret scanning failed. Remove secrets before committing."
        echo "  If this is a false positive, add an exclusion to .gitleaks.toml."
        exit 1
    fi
else
    echo "Warning: gitleaks not installed. Secret scanning skipped."
    echo "  Install: https://github.com/gitleaks/gitleaks/releases"
fi
```

`--staged` scans only files staged for the current commit, preventing secrets from
entering git history. See [Secrets Handling](./security/secrets-handling.md) for
installation, `.gitleaks.toml` false-positive configuration, and runtime patterns.

### File Size and Binary Restrictions

Append to any pre-commit hook, after secret scanning:

```bash
# Reject files larger than 10MB
git diff --cached --name-only | while read -r file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$size" -gt 10485760 ]; then
            echo "File $file exceeds 10MB ($size bytes). Use Git LFS or a package manager."
            exit 1
        fi
    fi
done

# Reject binary executables
if git diff --cached --name-only | grep -qE '\.(exe|dll|so|dylib)$'; then
    echo "Binary executables detected in staged files. Use package managers or build artifacts."
    exit 1
fi
```

## Commit Message Hook

All repositories enforce the [Conventional Commits](https://www.conventionalcommits.org/) format. This applies to JS/TS projects using Husky as well.

```bash
#!/usr/bin/env bash

commit_regex='^(feat|fix|docs|style|refactor|test|chore|security|perf)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "Commit message does not follow conventional commit format."
    echo ""
    echo "  Format:  type(scope): description"
    echo "  Types:   feat, fix, docs, style, refactor, test, chore, security, perf"
    echo ""
    echo "  Examples:"
    echo "    feat: add triage acquisition module"
    echo "    fix(auth): correct session token expiry"
    echo "    docs: update contributing guidelines"
    exit 1
fi

if grep -qiE "(security|vulnerability|cve|exploit|breach)" "$1"; then
    echo "Security-related commit. Ensure security review has been completed before pushing."
fi

echo "Commit message validated."
```

## Pre-Push Hook: Local CI/CD Gate + Claude Security Review

The pre-push hook runs two steps. Step 1 (`hooks/ci-check.sh`) is **blocking** — push aborts on failure. Step 2 (Claude Code security review) is **informational** — it displays findings but does not block the push.

### Requirements

- `hooks/ci-check.sh` present, containing the repository's lint/type-check/test/SAST/dependency checks (single source of truth, also called from `.github/workflows/ci.yml`)
- Claude Code CLI installed and authenticated (security review step only)
- `.claude/commands/security-review.md` present in the repository root (see Repo Template below)

### Hook

```bash
#!/usr/bin/env bash
# pre-push: local CI/CD gate + informational security review
#
# 1. hooks/ci-check.sh — same checks as .github/workflows/ci.yml.
#    BLOCKING: push aborts on failure. Local pass should reliably predict
#    the CI verdict for the same commit; GitHub Actions runs are
#    confirmation, not discovery.
# 2. Claude Code security review — semantic, informational only.
#    Findings are advisory; review them but they do not block the push.

set -e

echo "Running local CI checks (hooks/ci-check.sh)..."
bash hooks/ci-check.sh

echo ""
echo "Local CI checks passed."
echo ""

if ! command -v claude >/dev/null 2>&1; then
    echo "Claude Code not installed. Skipping security review."
    echo "  Install from: https://claude.ai/download"
    exit 0
fi

if [ ! -f ".claude/commands/security-review.md" ]; then
    echo ".claude/commands/security-review.md not found. Skipping security review."
    exit 0
fi

DIFF=$(git diff --merge-base origin/HEAD 2>/dev/null || git diff HEAD~1 2>/dev/null)

if [ -z "$DIFF" ]; then
    echo "No changes to review."
    exit 0
fi

echo "Running security review..."
PROMPT="$(cat .claude/commands/security-review.md)

DIFF:"
printf '%s\n%s\n' "$PROMPT" "$DIFF" | claude -p 2>&1 || echo "Security review failed to run (non-blocking)."

echo ""
echo "Security review complete. Address any findings above before pushing."
exit 0
```

The diff is piped to `claude -p` via stdin rather than passed as an argument — a large diff embedded directly in argv can exceed the OS argument-length limit (`Argument list too long`), and since this step runs under `set -e`, the resulting crash would block the push despite being documented as informational. The trailing `|| echo ...` guarantees the security-review step can never fail the push.

## JS/TS Projects: Husky

For JavaScript and TypeScript repositories, Husky manages the pre-commit hook. Husky requires Node.js and is scoped to JS/TS projects only — do not add it to Go, C, Python, or shell projects.

```json
{
  "devDependencies": {
    "husky": "^9.1.7",
    "lint-staged": "^15.5.0",
    "prettier": "^3.5.3"
  },
  "scripts": {
    "prepare": "husky",
    "pre-commit": "lint-staged"
  },
  "lint-staged": {
    "*.{js,ts,jsx,tsx}": ["eslint --fix", "prettier --write"],
    "*.{css,scss}": ["prettier --write"],
    "*.{html,md}": ["prettier --write"]
  }
}
```

The commit-msg and pre-push hooks above still apply to JS/TS projects. Wire them through Husky:

```bash
echo 'bash .git/hooks/commit-msg "$1"' > .husky/commit-msg
echo 'bash .git/hooks/pre-push' > .husky/pre-push
chmod +x .husky/commit-msg .husky/pre-push
```

## Forensic Evidence Tool Enhancements

For repositories subject to [Forensic Evidence Tool Standards](./Forensic%20Evidence%20Tool%20Standards.md), append to the pre-commit hook:

```bash
# Chain of custody notification
if git diff --cached --name-only | grep -qE "(evidence|forensic|acquisition)"; then
    echo "Forensic-related changes detected."
    echo "  Ensure proper chain of custody documentation is included."
    if ! git diff --cached --name-only | grep -qE "(CHAIN_OF_CUSTODY|EVIDENCE_LOG)"; then
        echo "  Consider adding chain of custody documentation."
    fi
fi

# Daubert compliance reminder
if git diff --cached --name-only | grep -qE "(analysis|algorithm|calculation)"; then
    echo "Changes may affect Daubert Standard compliance."
    echo "  Ensure proper documentation and validation testing."
fi
```

## Hook Installation

### Non-JS/TS Projects

The repo template provides hook files in `hooks/`. Copy and make executable:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
cp hooks/commit-msg .git/hooks/commit-msg
cp hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push
```

Customize `pre-commit` and `hooks/ci-check.sh` for the repository's language before copying. `hooks/ci-check.sh` is called by `hooks/pre-push`, not copied into `.git/hooks/` itself.

### JS/TS Projects

```bash
pnpm install
pnpm run prepare
# Wire commit-msg and pre-push as described in the Husky section above
```

## Repo Template

The [repo-template](../repo-template/) includes:

- `hooks/pre-commit` — language-neutral stub; customize per project
- `hooks/commit-msg` — conventional commits; copy as-is
- `hooks/ci-check.sh` — language-neutral stub; customize per project (single source of truth, also wired into `.github/workflows/ci.yml`)
- `hooks/pre-push` — local CI/CD gate + Claude security review; copy as-is
- `.claude/commands/security-review.md` — sourced from the [claude-code-security-review](https://github.com/anthropics/claude-code-security-review) repository; keep current with upstream
- `.gitattributes` — includes `/hooks/* text eol=lf` so hook shebangs survive on Windows checkouts

## Hook Bypass (Emergency Use Only)

```bash
git commit --no-verify -m "emergency: critical hotfix"
```

Document the bypass reason in the commit message and follow up with a compliant commit.

## CI/CD Integration

GitHub-public repositories replicate the pre-push security review in CI using the `claude-code-security-review` GitHub Action. The local pre-push hook and the GitHub Action are parallel mechanisms running the same review criteria in different contexts: Claude Code session locally, Claude API in CI.

For CI validation of commit message format:

```yaml
- name: Validate commit messages
  run: |
    git log --pretty=format:"%s" origin/main..HEAD | while read -r msg; do
      if ! echo "$msg" | grep -qE '^(feat|fix|docs|style|refactor|test|chore|security|perf)(\(.+\))?: .{1,50}'; then
        echo "Invalid commit message: $msg"
        exit 1
      fi
    done
```

## Maintenance

- Update language tooling versions in pre-commit hooks when project language versions change
- Re-source `.claude/commands/security-review.md` from upstream when significant updates are released
- Test hook changes in a scratch repository before deploying to active repos
- Husky version updates: test in JS/TS projects only

---

*This Git Hooks Standard integrates with Code Formatting Rules, Repository Security Rules, and GitHub Configuration Standards to provide automated enforcement of Positronikal coding standards.*
